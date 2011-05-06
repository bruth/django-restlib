from decimal import Decimal
from django.test import TestCase

from restlib.representations import json

__all__ = ('JSONRepresentationTestCase',)

class JSONRepresentationTestCase(TestCase):
    def setUp(self):
        self.tests = (
            ('{"foo": "bar"}', {u'foo': 'bar'}),
            ('{"foo": null}', {'foo': None}),
            ('[{"foo": null}, 5, null, 3.282]', [{'foo': None}, 5, None, 3.282]),
        )

    def test_encode(self):
        jsonrep = json.JSON()

        # FIXME this test fails before Python 2.7 due to the improvement
        # on float handling
        tests = (
            ('[1.34, 1.0, null]', [Decimal('1.34'), Decimal('1'), None]),
        )

        for x, y in self.tests + tests:
            self.assertEqual(jsonrep.encode(y, {}), x)

    def test_decode(self):
        jsonrep = json.JSON()

        for x, y in self.tests:
            self.assertEqual(jsonrep.decode(x, {}), y)
