from datetime import date

from restlib.tests import utils
from restlib.tests import models
from restlib.resources.model import get_or_create_resource


__all__ = ('FieldPseudoSelectorTestCase', 'ExcludePseudoSelectorTestCase')


class FieldPseudoSelectorTestCase(utils.BaseTestCase):
    def test_local(self):

        attrs = {'fields': (':local',)}

        BookResource, created = get_or_create_resource(models.Book, **attrs)

        self.assertEqual(BookResource.resolve_fields(self.book), {
            'id': 1,
            'title': 'Secrets of a JavaScript Ninja',
            'author': {'id': 1},
            'pub_date': date(2011, 6, 1),
            'tags': [{'id': 1}],
        })

    def test_related(self):
        attrs = {'fields': (':related',)}

        TagResource, created = get_or_create_resource(models.Tag, **attrs)

        self.assertEqual(TagResource.resolve_fields(self.tag1), {
            'book_set': [{'id': 1}],
            'hacker_set': [{'id': 1}],
            'library_set': [{'id': 1}],
        })

    def test_pk(self):
        attrs = {'fields': (':pk',)}

        TagResource, created = get_or_create_resource(models.Tag, **attrs)

        self.assertEqual(TagResource.resolve_fields(self.tag1), {
            'id': 1,
        })

    def test_nested(self):
        attrs = {
            'fields': (':local', ('book_set', ':local')),
            'exclude': (':pk', 'libraries', 'tags')
        }

        HackerResource, created = get_or_create_resource(models.Hacker, **attrs)

        self.assertEqual(HackerResource.resolve_fields(self.jresig), {
            'name': 'John Resig',
            'website': 'http://ejohn.org',
            'book_set': [{
                'id': 1,
                'title': 'Secrets of a JavaScript Ninja',
                'author': {'id': 1},
                'pub_date': date(2011, 6, 1),
                'tags': [{'id': 1}],
            }]
        })


class ExcludePseudoSelectorTestCase(utils.BaseTestCase):
    def test_local(self):

        attrs = {'fields': (':local', ':related'), 'exclude': (':related',)}

        BookResource, created = get_or_create_resource(models.Book, **attrs)

        self.assertEqual(BookResource.resolve_fields(self.book), {
            'id': 1,
            'title': 'Secrets of a JavaScript Ninja',
            'author': {'id': 1},
            'pub_date': date(2011, 6, 1),
            'tags': [{'id': 1}],
        })

    def test_related(self):
        attrs = {'fields': (':local', ':related'), 'exclude': (':local',)}

        TagResource, created = get_or_create_resource(models.Tag, **attrs)

        self.assertEqual(TagResource.resolve_fields(self.tag1), {
            'book_set': [{'id': 1}],
            'hacker_set': [{'id': 1}],
            'library_set': [{'id': 1}],
        })

    def test_pk(self):
        attrs = {'fields': (':local',), 'exclude': (':pk',)}

        TagResource, created = get_or_create_resource(models.Tag, **attrs)

        self.assertEqual(TagResource.resolve_fields(self.tag1), {
            'name': 'javascript',
        })
