from django.http import (HttpResponse, HttpResponseRedirect,
    HttpResponsePermanentRedirect, HttpResponseNotModified,
    HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden,
    HttpResponseNotAllowed, HttpResponseGone, HttpResponseServerError)

from restlib import http

class HttpResponseNotAcceptable(HttpResponse):
    status_code = 406

    def __init__(self, accepted_mimetypes):
        HttpResponse.__init__(self, ', '.join(accepted_mimetypes))


class HttpResponseUnsupportedMediaType(HttpResponse):
    status_code = 415

    def __init__(self):
        HttpResponse.__init__(self)
