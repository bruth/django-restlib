Django-RESTlib
==============

Define a Resource
-----------------
A ``Resource`` class is defined for each static or dynamic resource on the
server. The class provides a means of defining fine-grained expectations of
that resource.

What does that mean?

Django has a notion of site-wide middleware that is applied for all requests
and responses. This is obviously helpful in cases where the behavior across
resources is the same. When dealing with web APIs, finer grain control over the
resource may be required. Let's start with an example and break it down from
there:

```python
from restlib import http
from restlib import resources

class PostResource(resources.ModelResource):            # 1
    model = 'blog.Post'                                 # 2

    def GET(self, request, pk):                         # 3
        return self.queryset(request).get(pk=pk)

    def PUT(self, request, pk):                         # 4
        post = self.GET(request, pk)

        form = PostForm(request.data, instance=post)

        if form.is_valid():
            form.save()
            return http.NO_CONTENT                      # 5

        return http.CONFLICT, form.errors               # 6
```

``#1`` is the class definition. In this case, a Django model is the
resource being represented here, thus we use the ``ModelResource`` class
which contains additional features.

``#2`` defines that actual model being represented. It can be the class
itself or a string (as shown above) defining the app name and class name.
Regardless if a string is defined here, when the class is defined the actual
model class will be found and used.

``#3`` defines our first supported HTTP method for this resource (resources
are not assumed to support only ``OPTIONS`` by default), therefore ``GET``
requests can be made to this resource. If ``GET`` is defined, ``HEAD`` will
automatically be added to the resource.

``#4`` defines the second supported HTTP method for this resource. It performs
a simple form validation check using the existing instance.

``#5`` and ``#6`` shows two variations for returning a custom status code. The
first represents the status code for '204 No Content' which tells the client
the ``PUT`` was successful, but not content will be returned to the client.

The second form returns a '409 Conflict' which includes a custom error message
that will be sent as the content body of the response.  


Publish API
-----------
Resource classes can be hooked into Django's URLconfs the same way views are:

```python
    urlpatterns = patterns('blog.api',
        url(r'^blog/(?P<pk>\d+)/$', 'PostResource', name='post-resource')
    )
```


Resource Middleware
-------------------

Django has [middleware] [1] that is applied site-wide across all resources (views)
which is useful for applying common response headers, handling exceptions, etc.

RESTlib provides a way of defining middleware at the resource level. Certain
resources may require special handling depending on the function it serves. The
way to manage this currently with Django views is to _decorate_ views with
additional functionality, which includes things like ``@auth_required`` and
``@cache_page(60 * 60 * 24)``.

A simple middleware that will enable Cross-Origin Resource Sharing (CORS) can
defined like this:

```python
class CrossOriginResourceSharing(object):
    methods = ('OPTIONS',)

    preflight_headers = {
        'Access-Control-Allow-Origin': 'example.org' ,
        'Access-Control-Max-Age': '3600',
        'Access-Control-Allow-Methods': 'PUT',
    }

    def process_response(self, resource, request, response, **kwargs):
        for k, v in self.preflight_headers.iteritems():
            response[k.title()] = v
```

This middleware can be added to the list of middleware for a given resource:

```python
class PostResource(resources.ModelResource):
    model = 'blog.Post'

    middleware = (
        ...
        'middleware.CrossOriginResourceSharing',
        ...
    )
```

When browsers make non-simple requests to resources of different origin, they
typically perform a [preflight] [2] request (using ``OPTIONS``) to check if the
pending request is allowed to be made. This middleware ensures a given resource
is allowed to be accessed by clients located on the ``example.org`` domain for
1 hour at a time and for the non-simple method ``PUT``.

[1]: http://docs.djangoproject.com/en/dev/topics/http/middleware/
[2]: http://www.w3.org/TR/cors/#preflight-request
