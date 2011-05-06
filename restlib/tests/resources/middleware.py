class AjaxRequired(object):
    status_code = 404

    def process_request(self, request, **kwargs):
        if not request.is_ajax():
            return ''
