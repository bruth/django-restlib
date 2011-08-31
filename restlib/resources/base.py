import inspect

from django.template import Context
from django.http import HttpRequest, HttpResponse
from django.core import exceptions
from django.template.loader import get_template
from django.utils.importlib import import_module

from restlib import http
from restlib.conf import settings
from restlib.resources import utils
from restlib.representations import representation

__all__ = ('Resource', 'ResourceCollection')

def build_docstring(cls):
    """
    Generates a docstring incorporating all the attributes about
    the defined resource.
    """
    c = Context({
        'name': cls.__name__,
        'resource': cls,
    })

    t = get_template('restlib/docstring.txt')
    return t.render(c).strip()

def HEAD(self, request, *args, **kwargs):
    output = self.GET(request, *args, **kwargs)
    response = self._get_response(request, output)
    response.content = ''
    return response

def OPTIONS(self, request, *args, **kwargs):
    response = HttpResponse()
    response['Allow'] = ', '.join(self.allowed_methods)
    return response

def _setup_middleware(mcls, resource):
    allowed_methods = resource.allowed_methods

    processors = dict((method, {}) for method in allowed_methods)
    processors['__all__'] = {}

    # iterate over each middleware for the resource and load it if it
    # does not exist. cache each ``mw_instance`` as they are loaded
    for middleware_path in resource.middleware:
        if middleware_path not in mcls._middleware:
            if inspect.isclass(middleware_path):
                mw_instance = middleware_path()
            else:
                try:
                    dot = middleware_path.rindex('.')
                except ValueError:
                    raise exceptions.ImproperlyConfigured('%s isn\'t a middleware module' % middleware_path)

                mw_module, mw_classname = middleware_path[:dot], middleware_path[dot+1:]

                try:
                    mod = import_module(mw_module)
                except ImportError, e:
                    raise exceptions.ImproperlyConfigured('Error importing middleware %s: "%s"' % (mw_module, e))

                try:
                    mw_class = getattr(mod, mw_classname)
                except AttributeError:
                    raise exceptions.ImproperlyConfigured('Middleware module "%s" does not define a "%s" class' % (mw_module, mw_classname))

                try:
                    mcls._middleware[middleware_path] = mw_instance = mw_class()
                except exceptions.MiddlewareNotUsed:
                    continue
        else:
            mw_instance = mcls._middleware[middleware_path]

        # each resource middleware may define it's own set of
        # methods it is applicable too. fallback to all allowed
        # methods as defined by the resource
        methods = getattr(mw_instance, 'methods', None)

        for method in processors:
            # skip if the middleware defines a specific subset of 
            # methods that are applicable
            if methods and method not in methods:
                continue

            procs = processors[method]

            if hasattr(mw_instance, 'process_request'):
                procs.setdefault('process_request', [])
                procs['process_request'].append(mw_instance.process_request)

            if hasattr(mw_instance, 'process_response'):
                procs.setdefault('process_response', [])
                procs['process_response'].append(mw_instance.process_response)

        resource._middleware = processors


class ResourceMetaclass(type):
    """The base metaclass for ``Resource``. It sets and validates the
    ``allowed_methods`` attribute.
    """
    _cache = {}
    _middleware = {}

    def __new__(cls, name, bases, attrs):
        # create the new class so all inherited attributes have been set.
        new_cls = type.__new__(cls, name, bases, attrs)

        # perform further manipulation of the new class only if this does not
        # represent the base class defined locally
        if cls.__module__ != new_cls.__module__:

            # if HEAD is not already defined, use a sensible default
            if hasattr(new_cls, 'GET') and not hasattr(new_cls, 'HEAD'):
                new_cls.HEAD = HEAD

            # if ``allowed_methods`` is not defined explicitly in attrs, this
            # could mean one of two things: that the user wants it to inherit
            # from the parent class (if exists) or for it to be set implicitly.
            # the more explicit (and flexible) behavior will be to not inherit
            # it from the parent class, therefore the user must explicitly
            # re-set the attribute
            if 'allowed_methods' not in attrs:
                if not hasattr(new_cls, 'OPTIONS'):
                    new_cls.OPTIONS = OPTIONS

                allowed_methods = []

                for method in http.methods:
                    if callable(getattr(new_cls, method, None)):
                        allowed_methods.append(method)

            # ensure all methods that are allowed are actually defined
            else:
                allowed_methods = new_cls.allowed_methods

                if 'OPTIONS' in allowed_methods and not hasattr(new_cls, 'OPTIONS'):
                    new_cls.OPTIONS = OPTIONS

                # ensure all "said" ``allowed_methods`` actually exist
                for method in allowed_methods:
                    if getattr(new_cls, method, None) is None:
                        raise ValueError, ('the %s method is not defined '
                            'for the resource %s' % (method, name))

            new_cls.allowed_methods = tuple(allowed_methods)

            _setup_middleware(cls, new_cls)

            # the docstring rendering comes after populating all other
            # attributes since it depends on the complete set of attributes
            # that class expects to be set. note, the __doc__ is intentionally
            # checked in the new class' attributes since the docs should be
            # regenerated for every class
            if '__doc__' not in attrs:
                new_cls.__doc__ = build_docstring(new_cls)

            # add to the Resource cache for cross-resource referencing
            if new_cls not in cls._cache:
                cls._cache[new_cls] = len(cls._cache)

        return new_cls

    def __call__(cls, *args, **kwargs):
        """Tests to see if the first argument is an HttpRequest object, creates
        an instance, and calls it with the arguments.
        """
        if args and isinstance(args[0], HttpRequest):
            instance = super(ResourceMetaclass, cls).__call__()
            return instance.__call__(*args, **kwargs)
        return super(ResourceMetaclass, cls).__call__(*args, **kwargs)


class Resource(object):
    """The base Resource class which provides a simple interface for defining
    methods that correlate to the HTTP methods.

    ``allowed_methods`` - if this attribute is defined, it explicitly sets the
    type of HTTP requests that will be processed. If not defined, each method
    with the same name as an HTTP method will be allowed.

    ``mimetypes`` - a list of acceptable mimetypes that can be accepted
    and/or responded with. the precedence of a mimetype is defined by the
    position in the list with the 0th position having the highest precedence.
    """

    __metaclass__ = ResourceMetaclass

    mimetypes = ('application/json',)

    middleware = settings.RESOURCE_MIDDLEWARE

    def __call__(self, request, *args, **kwargs):
        method = request.method

        _response = self._process_request_middleware(request)
        if _response is not None:
            return _response

        try:
            # call the requested resource method
            output = getattr(self, method)(request, *args, **kwargs)
        except http.HttpStatusCode, e:
            output = e

        # get the response based on the Resource method's output
        response = self._get_response(request, output)

        _response = self._process_response_middleware(request, response)
        if _response is not None:
            return _response

        return response

    def _process_request_middleware(self, request):
        method = request.method

        # get all middleware for this method
        if method in self._middleware:
            procs = self._middleware[method]
        else:
            procs = self._middleware['__all__']

        # iterate over all request processors. if at any point the processor
        # returns a message that is not None, then we generate an HttpResponse
        # object and return it
        if procs.has_key('process_request'):
            for proc in procs['process_request']:
                mw_cls = proc.__self__

                try:
                    output = proc(resource=self, request=request)
                except http.HttpStatusCode, e:
                    output = e

                if output is not None:
                    if isinstance(output, HttpResponse):
                        return output

                    # custom method that may exist on the middleware class
                    # for generating an HttpResponse object
                    if hasattr(mw_cls, 'get_response'):
                        return mw_cls.get_response(message=output,
                            resource=self, request=request)

                    if not isinstance(output, http.HttpStatusCode):
                        output = (http.responses[mw_cls.status_code], output)

                    return self._get_response(request, output)

    def _process_response_middleware(self, request, response):
        method = request.method

        # get all middleware for this method
        if method in self._middleware:
            procs = self._middleware[method]
        else:
            procs = self._middleware['__all__']

        # iterate over all response processors. if at any point the processor
        # returns a message that is not None, then we generate an HttpResponse
        # object and return it
        if procs.has_key('process_response'):
            # iterate over all response processors
            for proc in procs['process_response']:
                mw_cls = proc.__self__

                try:
                    output = proc(resource=self, request=request, response=response)
                except http.HttpStatusCode, e:
                    output = e

                if output is not None:
                    if isinstance(output, HttpResponse):
                        return output

                    if hasattr(mw_cls, 'get_response'):
                        return mw_cls.get_response(message=output,
                            resource=self, request=request)

                    if not isinstance(output, http.HttpStatusCode):
                        output = (http.responses[mw_cls.status_code], output)

                    return self._get_response(request, output)

    def _get_response(self, request, output):
        """Handles various output types from HTTP method calls.

            1. HttpResponse instance
                - assume content has already been encoded

            2. HttpStatusCode instance
                - return a naked response without any content

            3. test for a two-item tuple containing an HttpStatusCode
            instance and the content
                - the status code defines the response type and the second
                argument defines an optional entity-body which will be encoded
                based on the 'Accept' header

            4. any other object
                - will use a standard 200 status code
                - this object will be encoded based on the 'Accept' header
        """

        status = None
        content = None
        streaming = False

        # response already defined, so just return 
        if isinstance(output, HttpResponse):
            return output

        # the status is returned, but with no content 
        if isinstance(output, http.HttpStatusCode):
            status = output.status_code

        # see if the output is a status/content pair, otherwise
        # assume the output is strictly content
        elif output and type(output) in (list, tuple):
            if isinstance(output[0], http.HttpStatusCode):
                status = output[0].status_code
                content = output[1]
            else:
                content = output

        # none of the basic parsing passed, therefore the output is
        # the content
        else:
            content = output

        # test for a stream-type object i.e. a generator. if true, then
        # do not process the content any further since it would be consumed
        if inspect.isgenerator(content):
            streaming = True

        # if there is content then handle it appropriately
        if content is not None:
            if hasattr(request, 'accepttype'):
                # if marked as streaming, this accepttype is the assumed output
                accepttype = request.accepttype

                if not streaming:
                    # attempt to resolve and encode the content based on the
                    # accepttype
                    content = self.resolve_fields(content)
                    content = representation.encode(accepttype, content)

                response = HttpResponse(content, status=status, mimetype=accepttype)
            else:
                response = HttpResponse(content, status=status)
        else:
            response = HttpResponse(status=status)

        if streaming:
            response.streaming = True

        return response

    # this is defined as a class method since it really is only referencing
    # class attributes and it may be referenced by another Resource while
    # being processed
    @classmethod
    def resolve_fields(cls, obj):
        return utils.convert_to_resource(obj)


class ResourceCollectionMetaclass(ResourceMetaclass):
    def __new__(cls, name, bases, attrs):
        # create the new class so all inherited attributes have been set.
        new_cls = super(ResourceCollectionMetaclass, cls).__new__(cls, name,
            bases, attrs)

        # perform further manipulation of the new class only if this does not
        # represent the base class defined locally
        if cls.__module__ != new_cls.__module__:
            if getattr(new_cls, 'resource', None) is None:
                raise AttributeError, 'No resource defined for %s' % name

            new_cls._resource = new_cls.resource()
        return new_cls


class ResourceCollection(Resource):
    """
    A ``ResourceCollection`` represents a collection of individual resources
    of the same type. That is, given a ``BookResource``, which defines
    attributes about that book e.g. title, author, etc., a
    ``BookResourceCollection`` would represent a collection of individual
    book resources.

    The attribute ``resource`` must be set denoting a ``Resource`` subclass
    that this collection is relative to.
    """

    __metaclass__ = ResourceCollectionMetaclass

