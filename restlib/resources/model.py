import inspect

from django.db import models
from django.db.models import loading
from django.utils.importlib import import_module

from restlib import http
from restlib.resources.base import (ResourceMetaclass, Resource,
    ResourceCollection, ResourceCollectionMetaclass)
from restlib.resources import utils


__all__ = ('ModelResource', 'ModelResourceCollection')

def _get_model(model):
    if isinstance(model, basestring):
        path = model.split('.')
        klass = path.pop()

        m = None
        # treat it as a normal model if path only contains the
        # app label
        if len(path) == 1:
            m = loading.get_model(path[0], klass)

        # fallback, if model not found in app
        if m is None:
            mod = import_module('.'.join(path))
            try:
                m = getattr(mod, klass)
            except AttributeError:
                pass

        if m is None:
            raise ImportError, '%s not found' % model

        model = m
    return model

class ModelResourceMetaclass(ResourceMetaclass):
    # an internal registry of all ModelResource classes defined. this is needed
    # to be able to do cross-resource references to implement HATEOAS or
    # reference the required fields for a related object.
    _defaults = {}

    def __new__(cls, name, bases, attrs):
        # get all attributes from bases which are not currently set
        new_cls = super(ModelResourceMetaclass, cls).__new__(cls, name, bases, attrs)

        # perform further manipulation of the new class only if this does not
        # represent the base class defined locally
        if cls.__module__ != new_cls.__module__:
            if not hasattr(new_cls, 'model') or new_cls.model is None:
                raise AttributeError, ('No model defined. If no model is necessary '
                    'define a Resource instead of a ModelResource')

            model = _get_model(new_cls.model)

            if not issubclass(model, models.Model):
                raise TypeError, 'Not a valid model'

            new_cls.model = model

            # populate all local fields for this model if not already defined.
            if not new_cls.fields:
                new_cls.fields = (':local',)

            new_cls.fields = utils.parse_attr_selectors(model, new_cls.fields,
                new_cls)

            # do not exclude anything by default
            if not new_cls.exclude:
                new_cls.exclude = ()

            new_cls.exclude = utils.parse_attr_selectors(model, new_cls.exclude,
                new_cls)

            # register the model and the associated ModelResource class
            if new_cls.default_for_related:
                if model in cls._defaults:
                    raise KeyError, 'default resource for "%s" already defined' % model.__name__
                cls._defaults[model] = new_cls

        return new_cls


class ModelResource(Resource):
    """
    The ``ModelResource`` provides some sensible defaults for the specified
    ``model``.

    ``model`` - a subclass of or path to a ``models.Model`` e.g.
    'myapp.SomeModel'
    """

    __metaclass__ = ModelResourceMetaclass

    # a tuple of fields to be used in the representation of this resource with
    # respect it's model. if ``fields`` evalutates ``False``, all local fields
    # and relationships will be included if possible. (related objects that
    # do not have a resource associated with them will only return there
    # ``id``s).
    fields = None

    # a list of fields to exclude when resolving them from the model class.
    # this takes precedence over the ``fields`` attribute.
    exclude = None

    # if the model this resource represents is referenced by a related object
    # during resolution of fields, this resource will be used to represent 
    # those model objects
    default_for_related = True

    @classmethod
    def queryset(cls, request):
        return cls.model._default_manager.all()

    @classmethod
    def get(cls, request, **kwargs):
        try:
            return cls.queryset(request).get(**kwargs)
        except cls.model.DoesNotExist:
            return None

    # this is defined as a class method since it really is only referencing
    # class attributes and it may be referenced by another Resource while
    # being processed
    @classmethod
    def resolve_fields(cls, obj):
        return utils.convert_to_resource(obj, resource=cls)

    def GET(self, request, pk):
        obj = self.get(request, pk=pk)
        if obj is None:
            return http.NOT_FOUND
        return obj


class ModelResourceCollectionMetaclass(ResourceCollectionMetaclass):
    def __new__(cls, name, bases, attrs):
        new_cls = super(ModelResourceCollectionMetaclass, cls).__new__(cls, name, bases, attrs)

        # perform further manipulation of the new class only if this does not
        # represent the base class defined locally
        if cls.__module__ != new_cls.__module__:
            if getattr(new_cls.resource, 'model', None) is None:
                raise TypeError, ('A ModelResource class or instance must be '
                    'defined (not a Resource).')

            resource = new_cls.resource

            if inspect.isclass(resource):
                new_cls.resource = resource()
                new_cls._resource_cls = resource
            else:
                new_cls.resource = resource
                new_cls._resource_cls = resource.__class__

            # conveniences
            new_cls.model = new_cls.resource.model
            new_cls.queryset = new_cls.resource.queryset
            new_cls.get = new_cls.resource.get

        return new_cls


class ModelResourceCollection(ResourceCollection):
    """
    The ``ModelResourceCollection`` provides additional utilites and defaults
    for requesting a collection of model resources.
    """

    __metaclass__ = ModelResourceCollectionMetaclass

    # this is defined as a class method since it really is only referencing
    # class attributes and it may be referenced by another Resource while
    # being processed
    @classmethod
    def resolve_fields(cls, obj):
        return utils.convert_to_resource(obj, resource=cls.resource)

    def GET(self, request):
        return self.queryset(request)


def get_or_create_resource(model, force=False, **attrs):
    created = False
    resource = ModelResourceMetaclass._defaults.get(model, None)

    if force or not resource:
        created = True

        cls = ModelResourceMetaclass
        name = '%s%s' % (model.__name__, 'Resource')
        bases = (ModelResource,)
        attrs.update({
            'model': model,
            'default_for_related': False
        })

        resource = cls.__new__(cls, name, bases, attrs)

    return resource, created

