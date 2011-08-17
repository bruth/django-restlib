from django.test import TestCase
from django.http import HttpRequest

from restlib import resources, http


__all__ = ('HttpExceptionTestCase',)


class Middleware(object):
    methods = ('DELETE',)

    status_code = 200

    def process_request(self, resource, request):
        raise http.FORBIDDEN


class Resource(resources.Resource):
    middleware = (Middleware,)

    def GET(self, request):
        raise http.NOT_FOUND

    def DELETE(self, request):
        pass


class HttpExceptionTestCase(TestCase):
    def test_exception(self):
        request = HttpRequest()
        request.method = 'GET'
        response = Resource(request)
        self.assertEqual(response.status_code, 404)

    def test_middleware_exception(self):
        request = HttpRequest()
        request.method = 'DELETE'
        response = Resource(request)
        self.assertEqual(response.status_code, 403)
