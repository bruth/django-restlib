from django.test import TestCase
from django.http import HttpRequest, HttpResponse

from restlib import http
from restlib import resources
from restlib.tests.models import Tag

__all__ = ('ResourceTestCase',)


class Object(object):
    pass


class ResourceTestCase(TestCase):
    def setUp(self):
        Tag(name='Python').save()
        Tag(name='REST').save()

        class A(resources.Resource):
            pass

        class B(resources.Resource):
            allowed_methods = ('GET', 'POST', 'PUT')

            def GET(self, request):
                return Tag.objects.all()

            def POST(self, request):
                return 'Created'

            def PUT(self, request):
                return 'Updated'

        class C(resources.Resource):
            middleware = (
                'restlib.resources.middleware.client.MethodNotAllowed',
                'restlib.tests.resources.middleware.AjaxRequired',
                'restlib.resources.middleware.client.UnsupportedMediaType',
                'restlib.resources.middleware.client.UnprocessableEntity',
            )

            def POST(self, request):
                return http.CREATED

        class D(resources.Resource):
            middleware = (
                'restlib.resources.middleware.client.Unauthorized',
                'restlib.resources.middleware.client.MethodNotAllowed',
                'restlib.resources.middleware.client.UnsupportedMediaType',
                'restlib.resources.middleware.client.UnprocessableEntity',
            )

            def GET(self, request):
                return HttpResponse('Hello World!')

        self.a = A()
        self.b = B()
        self.c = C()
        self.d = D()

    def test_allowed_methods(self):
        self.assertTrue(all([x in self.a.allowed_methods for x in ('OPTIONS',)]))
        self.assertTrue(all([x in self.b.allowed_methods for x in ('GET', 'POST', 'PUT')]))
        self.assertTrue(all([x in self.c.allowed_methods for x in ('POST', 'OPTIONS')]))
        self.assertTrue(all([x in self.d.allowed_methods for x in ('GET', 'HEAD', 'OPTIONS')]))

    def test_not_allowed(self):
        request = HttpRequest()
        request.method = 'DELETE'

        response = self.b(request)
        self.assertEqual(response.status_code, http.METHOD_NOT_ALLOWED)
        self.assertEqual(response['Allow'], ', '.join(self.b.allowed_methods))

    def test_ajax_required(self):
        request = HttpRequest()
        request.method = 'POST'

        response = self.c(request)
        self.assertEqual(response.status_code, http.NOT_FOUND)

        request.META['HTTP_X_REQUESTED_WITH'] = u'XMLHttpRequest'
        request.META['CONTENT_TYPE'] = 'application/json'
        request._raw_post_data = '{"name": "John Doe", "age": 37}'

        response = self.c(request)
        self.assertEqual(request.data, {'name': 'John Doe', 'age': 37})
        self.assertEqual(response.status_code, http.CREATED)

    def test_auth_required(self):
        request = HttpRequest()
        request.method = 'GET'

        response = self.d(request)
        self.assertEqual(response.status_code, http.UNAUTHORIZED.code)

    def test_head(self):
        request = HttpRequest()
        request.user = Object()
        request.user.is_authenticated = lambda: True

        response = self.d(request)
        self.assertEqual(response.content, '')
        self.assertEqual(response['Allow'], ', '.join(self.d.allowed_methods))

        request.method = 'HEAD'
        response = self.d(request)

    def test_options(self):
        request = HttpRequest()
        request.method = 'OPTIONS'
        request.META['HTTP_ACCEPT'] = 'application/json'

        response = self.a(request)
        self.assertEqual(response['Allow'], 'OPTIONS')

    def test_mimetype(self):
        request = HttpRequest()
        request.method = 'GET'
        request.META['HTTP_ACCEPT'] = '*/*'

        self.b(request)
        self.assertEqual(request.accepttype, 'application/json')

        request = HttpRequest()
        request.method = 'PUT'
        request.META['CONTENT_TYPE'] = 'application/json; charset=utf-8'
        request._raw_post_data = '{"name": "Sally Doe", "age": null}'

        self.b(request)
        self.assertEqual(request.contenttype, 'application/json')
        self.assertTrue(hasattr(request, 'PUT'))

    def test_resolver(self):
        request = HttpRequest()
        request.method = 'GET'
        request.META['HTTP_ACCEPT'] = '*/*'

        response = self.b(request)
        self.assertEqual(response.content, '[{"id": 1}, {"id": 2}]')
