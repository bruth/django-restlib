from django.http import HttpResponse

from restlib import http
from restlib.resources import utils
from restlib.representations import representation

class BadRequest(object):
    status_code = 400

    def get_response(self, resource, request):
        return HttpResponse(status=self.status_code)

    def process_request(self, resource, request, **kwargs):
        pass

class Unauthorized(object):
    status_code = 401

    def process_request(self, resource, request, **kwargs):
        if not hasattr(request, 'user') or not request.user.is_authenticated():
            return ''


class Forbidden(object):
    status_code = 403

    def process_request(self, resource, request, **kwargs):
        return ''


class MethodNotAllowed(object):
    status_code = 405

    def process_request(self, resource, request, **kwargs):
        if request.method not in resource.allowed_methods:
            response = HttpResponse(status=self.status_code)
            response['Allow'] = ', '.join(resource.allowed_methods)
            return response


class NotAcceptable(object):
    status_code = 406

    def process_request(self, resource, request, **kwargs):
        accepttype = utils.get_accepttype(request, resource.mimetypes)

        # augment request object with the mimetype required by the 'Accept'
        # header. this value will be None if a match is not determined
        if not accepttype or not representation.supports_encoding(accepttype):
            return HttpResponse(', '.join(resource.mimetypes),
                status=self.status_code)


class RequestURITooLong(object):
    status_code = 414

    def process_request(self, resource, request, **kwargs):
        return ''


class UnsupportedMediaType(object):
    methods = ('POST', 'PUT', 'PATCH')
    status_code = 415

    def process_request(self, resource, request, **kwargs):
        method = request.method

        # coerce POST to PUT if necessary
        if method == http.PUT:
            utils.coerce_post_put(request)

        contenttype = utils.get_contenttype(request, resource.mimetypes)

        # If a decoder for this type is not found, the request will be
        # stopped from further processing and return a 'Unsupported Media
        # Type' code as defined here: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.7
        # with a list of accepted mimetypes.
        if not contenttype or not representation.supports_decoding(contenttype):
            return ''


class UnprocessableEntity(object):
    methods = ('POST', 'PUT', 'PATCH')
    status_code = 422

    def process_request(self, resource, request, **kwargs):
        # this, in theory, should never occur if UnsupportedMediaType preceeds,
        # but you never know..
        if not hasattr(request, 'contenttype'):
            return

        payload = request.raw_post_data

        try:
            request.data = representation.decode(request.contenttype, payload)
        except Exception:
            return ''


class CrossOriginResourceSharing(object):
    methods = ('OPTIONS',)

    preflight_headers = {}

    def process_response(self, resource, request, response, **kwargs):
        # add all the necessary headers to the pre-flight request
        for k, v in self.preflight_headers.iteritems():
            response[k.title()] = v

