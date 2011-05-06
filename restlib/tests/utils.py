from datetime import date

from django.test import TestCase

from restlib.tests import models
from restlib.resources.model import (ResourceMetaclass,
    ModelResourceMetaclass)

class BaseTestCase(TestCase):
    def setUp(self):

        self.old_defaults = ModelResourceMetaclass._defaults
        self.old_cache = ResourceMetaclass._cache
        ModelResourceMetaclass._defaults = {}
        ResourceMetaclass._cache = {}

        self.jresig = models.Hacker(name='John Resig', website='http://ejohn.org')
        self.jresig.save()

        self.jquery = models.Library(name='jQuery', url='http://jquery.com',
            language='JavaScript')
        self.jquery.save()

        self.jresig.libraries.add(self.jquery)

        self.book = models.Book(title='Secrets of a JavaScript Ninja', author=self.jresig,
            pub_date=date(2011, 6, 1))
        self.book.save()

        self.tag1 = models.Tag(name='javascript')
        self.tag1.save()

        self.jresig.tags.add(self.tag1)
        self.jquery.tags.add(self.tag1)
        self.book.tags.add(self.tag1)

    def tearDown(self):
        ModelResourceMetaclass._defaults = self.old_defaults
        ResourceMetaclass._cache = self.old_cache

