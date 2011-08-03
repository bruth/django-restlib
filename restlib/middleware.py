from django.conf import settings
from django.middleware.http import ConditionalGetMiddleware
from django.middleware.common import CommonMiddleware

class StreamingCommonMiddleware(CommonMiddleware):
    def process_response(self, request, response):
        streaming = getattr(request, 'streaming', False)

        # this is a simple way to spoof the logic in CommonMiddleware, so the
        # content is not consumed in the md5 digest. this will never match the
        # 'If-None-Match' header, thus it will not return a 304 'Not Modified'
        # status code. we simply set a dummy ETag and then remove it afterwards
        # so as to not pollute the response
        if streaming and settings.USE_ETAGS:
            response['ETag'] = ''
            # response modified in-place
            super(StreamingCommonMiddleware, self).process_response(request, response)

            del response['ETag']
            return response

        # all other scenarios here can be processed as normal since they do not
        # affect streaming content
        return super(StreamingCommonMiddleware, self).process_response(request, response)


class StreamingConditionalGetMiddleware(ConditionalGetMiddleware):
    def process_response(self, request, response):
        streaming = getattr(request, 'streaming', False)

        # spoofs the logic for setting the 'Content-Length' so the response
        # content is not consumed
        if streaming:
            response['Content-Length'] = None
            # response modified in-place
            super(StreamingConditionalGetMiddleware, self).process_response(request, response)

            del response['Content-Length']
            return response

        # all other scenarios here can be processed as normal since they do not
        # affect streaming content
        return super(StreamingConditionalGetMiddleware, self).process_response(request, response)
