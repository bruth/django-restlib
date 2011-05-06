from restlib import mimeparse
from restlib.constants import ANY_MIMETYPE, DEFAULT_CONTENTTYPE

def mimetype_supported(mimetype, mimetypes):
    """Performs the handy work of determining the best match between the given
    mimetype and the list of mimetypes that are supported.
    """
    if not mimetype:
        return DEFAULT_CONTENTTYPE
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
    match = mimetype_supported(mimetype, mimetypes)

    request.contenttype = match
    return (match is not None, match)

def get_accepttype(request, mimetypes):
    """
    Checks to see if the request's 'Accept' header is a supported encoding
    for this resource. The 'Accept' header is parsed to determine and compared
    against the list of defined mimetypes.

    The request object is augmented with a ``accepttype`` attribute for
    further processing downstream.
    """
    mimetype = request.META.get('HTTP_ACCEPT', None)
    if mimetype is None:
        # assume an acceptable type is the contenttype is one is supplied.
        # this requires the contenttype processing be done before the
        # accepttype
        if hasattr(request, 'contenttype'):
            mimetype = request.contenttype
        else:
            mimetype = ANY_MIMETYPE

    match = mimetype_supported(mimetype, mimetypes)

    request.accepttype = match
    return match

def coerce_post_put(request):
    request.PUT = request.POST
    request.POST = None
