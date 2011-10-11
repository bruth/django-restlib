from django.http import HttpResponse

class HttpMethod(object):
    """An HTTP method which defines whether this method is safe and
    idempotent.

    ref: http://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html
    """
    def __init__(self, method, safe, idempotent):
        self.method = method
        self.safe = safe
        self.idempotent = idempotent

    def __str__(self):
        return self.method

    def __repr__(self):
        props = []

        if self.safe:
            props.append('Safe')
        if self.idempotent:
            props.append('Idempotent')

        if props:
            return '<HttpMethod: %s ()>' % (str(self), ', '.join(props))
        return '<HttpMethod: %s>' % str(self)

    def __eq__(self, obj):
        if isinstance(obj, basestring):
            return obj == str(self)
        return super(HttpMethod, self).__cmp__(obj)


class HttpStatusCode(Exception):
    """HTTP response status code which may be used within ``Resource``
    methods for constructing a response.

    ref: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
    """
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __repr__(self):
        return '<HttpStatusCode: %s (%d)>' % (self.message, self.status_code)

    def __eq__(self, obj):
        return obj == self.status_code

    def __call__(self, content='', mimetype=None, **headers):
        resp = HttpResponse(content, status=self.status_code, mimetype=mimetype)
        for key, value in headers.items():
            resp[key.replace('_', '-').title()] = value
        return resp


GET     = HttpMethod('GET', True, True)
HEAD    = HttpMethod('HEAD', True, True)
OPTIONS = HttpMethod('OPTIONS', True, True)
TRACE   = HttpMethod('TRACE', True, True)
PUT     = HttpMethod('PUT', False, True)
DELETE  = HttpMethod('DELETE', False, True)
POST    = HttpMethod('POST', False, False)

# PATCH Method introduced; ref: http://tools.ietf.org/html/rfc5789
PATCH   = HttpMethod('PATCH', False, False)

methods = dict((str(x), x) for x in
    (OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, PATCH))

# Informational 1xx
CONTINUE = HttpStatusCode(100, 'Continue')
SWITCHING_PROTOCOLS = HttpStatusCode(101, 'Switching Protocols')

# Successful 2xx
OK = HttpStatusCode(200, 'OK')
CREATED = HttpStatusCode(201, 'Created')
ACCEPTED = HttpStatusCode(202, 'Accepted')
NON_AUTHORITATIVE_INFORMATION = HttpStatusCode(203, 'Non-Authoritative Information')
NO_CONTENT = HttpStatusCode(204, 'No Content')
RESET_CONTENT = HttpStatusCode(205, 'Reset Content')
PARTIAL_CONTENT = HttpStatusCode(206, 'Partial Content')

# Redirection 3xx
MULTIPLE_CHOICES = HttpStatusCode(300, 'Multiple Choices')
MOVED_PERMANENTLY = HttpStatusCode(301, 'Moved Permanently')
FOUND = HttpStatusCode(302, 'Found')
SEE_OTHER = HttpStatusCode(303, 'See Other')
NOT_MODIFIED = HttpStatusCode(304, 'Not Modified')
USE_PROXY = HttpStatusCode(305, 'Use Proxy')
# UNKNOWN = HttpStatusCode(306, 'Unknown')
TEMPORARY_REDIRECT = HttpStatusCode(307, 'Temporary Redirect')

# Client Errors 4xx
BAD_REQUEST = HttpStatusCode(400, 'Bad Request')
UNAUTHORIZED = HttpStatusCode(401, 'Unauthorized')
PAYMENT_REQUIRED = HttpStatusCode(402, 'Payment Required')
FORBIDDEN = HttpStatusCode(403, 'Forbidden')
NOT_FOUND = HttpStatusCode(404, 'Not Found')
METHOD_NOT_ALLOWED = HttpStatusCode(405, 'Method Not Allowed')
NOT_ACCEPTABLE = HttpStatusCode(406, 'Not Acceptable')
PROXY_AUTHENTICATION_REQUIRED = HttpStatusCode(407, 'Proxy Authentication Required')
REQUEST_TIMEOUT = HttpStatusCode(408, 'Request Timeout')
CONFLICT = HttpStatusCode(409, 'Conflict')
GONE = HttpStatusCode(410, 'Gone')
LENGTH_REQUIRED = HttpStatusCode(411, 'Length Required')
PRECONDITION_FAILED = HttpStatusCode(412, 'Precondition Failed')
REQUEST_ENTITY_TOO_LARGE = HttpStatusCode(413, 'Request Entity Too Large')
REQUEST_URI_TOO_LONG = HttpStatusCode(414, 'Request-URI Too Long')
UNSUPPORTED_MEDIA_TYPE = HttpStatusCode(415, 'Unsupported Media Type')
REQUESTED_RANGE_NOT_SATISFIABLE = HttpStatusCode(416, 'Requested Range Not Satisfiable')
EXPECTATION_FAILED = HttpStatusCode(417, 'Expectation Failed')
UNPROCESSABLE_ENTITY = HttpStatusCode(422, 'Unprocessable Entity')

# Server Errors 5xx
INTERNAL_SERVER_ERROR = HttpStatusCode(500, 'Internal Server Error')
NOT_IMPLEMENTED = HttpStatusCode(501, 'Not Implemented')
BAD_GATEWAY = HttpStatusCode(502, 'Bad Gateway')
SERVICE_UNAVAILABLE = HttpStatusCode(503, 'Service Unavailable')
GATEWAY_TIMEOUT = HttpStatusCode(504, 'Gateway Timeout')
HTTP_VERSION_NOT_SUPPORTED = HttpStatusCode(505, 'HTTP Version Not Supported')

responses = {
    100: CONTINUE,
    101: SWITCHING_PROTOCOLS,
    200: OK,
    201: CREATED,
    202: ACCEPTED,
    203: NON_AUTHORITATIVE_INFORMATION,
    204: NO_CONTENT,
    205: RESET_CONTENT,
    206: PARTIAL_CONTENT,
    300: MULTIPLE_CHOICES,
    301: MOVED_PERMANENTLY,
    302: FOUND,
    303: SEE_OTHER,
    304: NOT_MODIFIED,
    305: USE_PROXY,
    # 306: UNKNOWN,
    307: TEMPORARY_REDIRECT,
    400: BAD_REQUEST,
    401: UNAUTHORIZED,
    402: PAYMENT_REQUIRED,
    403: FORBIDDEN,
    404: NOT_FOUND,
    405: METHOD_NOT_ALLOWED,
    406: NOT_ACCEPTABLE,
    407: PROXY_AUTHENTICATION_REQUIRED,
    408: REQUEST_TIMEOUT,
    409: CONFLICT,
    410: GONE,
    411: LENGTH_REQUIRED,
    412: PRECONDITION_FAILED,
    413: REQUEST_ENTITY_TOO_LARGE,
    414: REQUEST_URI_TOO_LONG,
    415: UNSUPPORTED_MEDIA_TYPE,
    416: REQUESTED_RANGE_NOT_SATISFIABLE,
    417: PRECONDITION_FAILED,
    422: UNPROCESSABLE_ENTITY,
    500: INTERNAL_SERVER_ERROR,
    501: NOT_IMPLEMENTED,
    502: BAD_GATEWAY,
    503: SERVICE_UNAVAILABLE,
    504: GATEWAY_TIMEOUT,
    505: HTTP_VERSION_NOT_SUPPORTED,
}
