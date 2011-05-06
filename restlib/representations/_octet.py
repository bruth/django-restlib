class OctetStream(object):
    def encode(self, obj, *args, **kwargs):
        return str(obj)

    def decode(self, obj, *args, **kwargs):
        return obj
