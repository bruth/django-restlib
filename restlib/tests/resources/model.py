from django.test import TestCase
from django.db import models

from restlib import resources
from restlib.resources.model import ModelResourceMetaclass
from restlib.tests.models import Hacker, Library, Book


__all__ = ('MetaclassTestCase',)


class BookResource(resources.ModelResource):
    model = Book


class HackerResource(resources.ModelResource):
    model = Hacker


class LibraryResource(resources.ModelResource):
    model = Library


class MetaclassTestCase(TestCase):
    def test_populate(self):
        klasses = ModelResourceMetaclass._defaults.keys()
        names = sorted([m.__name__ for m in klasses])

        self.assertEqual(names, ['Book', 'Hacker', 'Library', 'SomeModel'])

    def test_update(self):
        class Location(models.Model):
            pass

        class LocationResource(resources.ModelResource):
            model = Location

        self.assertTrue(Location in ModelResourceMetaclass._defaults)



