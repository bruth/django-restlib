class InternalServerError(object):
    status_code = 500

    def process_request(self, resource, request, **kwargs):
        pass


class NotImplemented(object):
    status_code = 501

    def process_request(self, resource, request, **kwargs):
        pass


class ServiceUnavailable(object):
    status_code = 503

    def process_request(self, resource, request, **kwargs):
        pass
