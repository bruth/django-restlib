import warnings

from restlib.representations import _json, _plain, _octet, _xml, _www

class Representation(object):
    library = {}

    def __contains__(self, key):
        return key in self.library

    @classmethod
    def register(cls, mimetype, klass):
        if mimetype in cls.library:
            warnings.warn('Re-registering for %s' % mimetype)

        cls.library[mimetype] = klass()

    @classmethod
    def unregister(cls, mimetype):
        cls.library.pop(mimetype, None)

    def encode(self, mimetype, data, **kwargs):
        if mimetype not in self.library:
            raise KeyError, 'Encoder for %s not registered' % mimetype
        return self.library[mimetype].encode(data, **kwargs)

    def decode(self, mimetype, data, **kwargs):
        if mimetype not in self.library:
            raise KeyError, 'Decoder for %s not registered' % mimetype
        return self.library[mimetype].decode(data, **kwargs)

    def supports_encoding(self, mimetype):
        if mimetype not in self:
            return None
        return hasattr(self.library[mimetype], 'encode')

    def supports_decoding(self, mimetype):
        if mimetype not in self:
            return None
        return hasattr(self.library[mimetype], 'decode')

representation = Representation()

# register built-in representation encoders/decoders
representation.register('application/x-www-form-urlencoded', _www.UrlEncoded)
representation.register('application/octet-stream', _octet.OctetStream)
representation.register('text/plain', _plain.PlainText)
representation.register('application/json', _json.JSON)
representation.register('application/xml', _xml.DataOrientedXML)
