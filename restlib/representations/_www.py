from django.http import QueryDict

class UrlEncoded(object):
    def decode(self, data):
        return QueryDict(data)
