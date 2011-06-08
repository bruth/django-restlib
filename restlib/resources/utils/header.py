from restlib import mimeparse
from restlib.constants import ANY_MIMETYPE, DEFAULT_CONTENTTYPE

def mimetype_supported(mimetype, mimetypes):
    """Performs the handy work of determining the best match between the given
    mimetype and the list of mimetypes that are supported.
    """
    # early return if all mimetypes are accepted
    if mimetype == ANY_MIMETYPE:
        return mimetypes[0]
    # precedence for ``mimeparse.best_match`` is opposite of how
    # they are defined in Resource, so we reverse it
    mimetypes = list(mimetypes)
    mimetypes.reverse()
    match = mimeparse.best_match(mimetypes, mimetype)
    return match

def get_contenttype(request, mimetypes):
    """
    Checks to see if the request's entity format is supported for this resource.
    The 'Content-Type' header is parsed to determine and compared against
    the list of defined mimetypes.

    The request object is augmented with a ``contenttype`` attribute for
    further processing downstream.
    """
    mimetype = request.META.get('CONTENT_TYPE', None)

    if not mimetype:
        match = DEFAULT_CONTENTTYPE
    else:
        match = mimetype_supported(mimetype, mimetypes)

    request.contenttype = match
    return match

def get_accepttype(request, mimetypes):
    """
    Checks to see if the request's 'Accept' header is a supported encoding
    for this resource. The 'Accept' header is parsed to determine and compared
    against the list of defined mimetypes.

    The request object is augmented with a ``accepttype`` attribute for
    further processing downstream.
    """
    mimetype = request.META.get('HTTP_ACCEPT', None)

    # assume an acceptable type is the contenttype is one is supplied.
    # this requires the contenttype processing be done before the
    # accepttype
    if not mimetype and getattr(request, 'contenttype', None):
        mimetype = request.contenttype

    if mimetype:
        match = mimetype_supported(mimetype, mimetypes)
        request.accepttype = match
    else:
        match = None

    return match

def coerce_post_put(request):
    request.PUT = request.POST
    request.POST = None
