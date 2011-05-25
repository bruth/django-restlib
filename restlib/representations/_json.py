from datetime import datetime, date, time
from decimal import Decimal
from django.utils import simplejson
from django.conf import settings

DATE_FORMAT = '%m/%d/%Y'
TIME_FORMAT = '%H:%M:%S'

class EnhancedJSONEncoder(simplejson.JSONEncoder):
    "Enhances the default JSONEncoder to handle other Python types."
    def default(self, obj):

        if isinstance(obj, set):
            return list(set)

        if isinstance(obj, Decimal):
            return float(str(obj))

        if isinstance(obj, datetime):
            return obj.strftime('%s %s' % (DATE_FORMAT, TIME_FORMAT))

        if isinstance(obj, date):
            return obj.strftime(DATE_FORMAT)

        if isinstance(obj, time):
            return obj.strftime(TIME_FORMAT)

        return super(EnhancedJSONEncoder, self).default(obj)


class EnhancedJSONDecoder(simplejson.JSONDecoder):
    "Enhances the default JSONDecoder to handles other Python types."
    # TODO determine if date and times are worth supporting. my initial
    # gut is no since it is unknown whether the data is going to be handled
    # as strings (e.g. saved off in a database) or used as Python objects.
    # also, there will be a large performance hit for large objects since
    # *every* string would have to be tested to see if it matches a datetime
    # format.
    def default(self, obj):
        return super(EnhancedJSONDecoder, self).default(obj)


class JSON(object):
    """
    Very basic JSON representation encode/decoder. Additional Python types are
    supported via a encoder subclass including: set, Decimal, datetime, date
    and time objects.
    """
    encode_options = {}
    decode_options = {}

    if settings.DEBUG:
        encode_options = {
            'indent': 4,
            'sort_keys': True,
        }

    def encode(self, data, options=None, **kwargs):
        if options is None:
            options = self.encode_options
        return simplejson.dumps(data, cls=EnhancedJSONEncoder, **options)

    def decode(self, data, options=None, **kwargs):
        if options is None:
            options = self.decode_options
        return simplejson.loads(data, cls=EnhancedJSONDecoder, **options)

