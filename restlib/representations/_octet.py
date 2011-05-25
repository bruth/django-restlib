class OctetStream(object):
    def encode(self, obj, **kwargs):
        return str(obj)

    def decode(self, obj, **kwargs):
        return obj
