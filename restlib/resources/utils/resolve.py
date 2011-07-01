from django.db import models
from django.db.models.query import QuerySet

from restlib.conf import settings

PSEUDO_SELECTORS = (':all', ':pk', ':local', ':related')

class ModelFieldResolver(object):
    cache = {}

    def _get_pk_field(self, model):
        fields = (model._meta.pk,)
        names = tuple(map(lambda x: x.name, fields))

        return {
            ':pk': dict(zip(names, fields)),
        }

    def _get_local_fields(self, model):
        "Return the names of all locally defined fields on the model class."
        local = model._meta.fields
        m2m = model._meta.many_to_many

        fields = tuple(local + m2m)
        names = tuple(map(lambda x: x.name, fields))

        return {
            ':local': dict(zip(names, fields)),
        }

    def _get_related_fields(self, model):
        "Returns the names of all related fields for model class."
        reverse_fk = model._meta.get_all_related_objects()
        reverse_m2m = model._meta.get_all_related_many_to_many_objects()

        fields = tuple(reverse_fk + reverse_m2m)
        names = tuple(map(lambda x: x.get_accessor_name(), fields))

        return {
            ':related': dict(zip(names, fields)),
        }

    def _get_fields(self, model):
        if not self.cache.has_key(model):
            fields = {}

            fields.update(self._get_pk_field(model))
            fields.update(self._get_local_fields(model))
            fields.update(self._get_related_fields(model))

            all_ = {}
            for x in fields.values():
                all_.update(x)

            fields[':all'] = all_

            self.cache[model] = fields

        return self.cache[model]

    def get_local_model_field(self, model, attr):
        fields = self._get_fields(model)

        if attr in PSEUDO_SELECTORS:
            return fields[attr].keys()

        elif attr in fields[':local']:
            return fields[':local'][attr]

        elif hasattr(model, attr):
            return attr

    def get_model_relation(self, model, attr):
        fields = self._get_fields(model)

        if attr in fields[':all']:
            related = fields[':all'][attr]
            if isinstance(related, models.ManyToManyField):
                return related.rel.to
            return related.model


resolver = ModelFieldResolver()

def parse_attr_selectors(model, attrs, resource):
    """Recursively verifies all of ``attrs`` for the given model (and related
    models) exist. It also substitutes any pseduo-selectors present with the
    attribute names.
    """
    level = []
    for attr in attrs:
        # this implies traversing through a related object
        if type(attr) in (tuple, list):
            related = resolver.get_model_relation(model, attr[0])
            if related is None:
                continue
            node = (attr[0],) + parse_attr_selectors(related, attr[1:], resource)

            level.append(node)
        else:
            # reference to the original attribute string
            node = attr

            # this implies a mapping, e.g. get_absolute_url->uri, which refers
            # to get_absolute_url as being the attr/func of interest, but the
            # resulting attribute name will be uri
            if '->' in attr:
                attr, name = attr.split('->')

            field = resolver.get_local_model_field(model, attr)

            # fallback to checking if the resource has a local method defined
            # by this name
            if field is None and not hasattr(resource, attr):
                if settings.IGNORE_MISSING_FIELDS:
                    continue

                raise AttributeError, 'The "%s" attribute could not be found '\
                    'on the model "%s" nor the resource "%s"' % (attr, model,
                    resource)

            if type(field) is list:
                level.extend(field)
            else:
                level.append(node)

    return tuple(level)


def get_resource_for_model(model, fields=None):
    """Gets the default resource for this model. This should only be used when
    dealing with related objects. This is invoked when a resource associated
    with this model does not exist.
    """
    from restlib.resources.model import get_or_create_resource

    # these two lines may seem confusing, but if fields are already defined,
    # this will force the creation of a new resource since it explicitly
    # defines fields. the second line is to fallback to just the ``pk``
    # field of the ``model``
    force = True if fields else False
    fields = fields or (':pk',)

    return get_or_create_resource(model, force=force,
        fields=fields)


def queryset_to_resource(obj, resource=None, fields=None, depth=0):
    model = obj.model

    if resource is None:
        resource, created = get_resource_for_model(model, fields=fields)

    return [model_to_resource(x, resource=resource) for x in iter(obj)]


def model_to_resource(obj, resource=None, fields=None, depth=0):
    """Takes a model object or queryset and converts it into a native object
    given the list of attributes either local or related to the object.
    """
    from restlib.resources import ModelResource

    if resource is None or not (isinstance(resource, ModelResource) or
        issubclass(resource, ModelResource)):
        resource, created = get_resource_for_model(obj.__class__, fields=fields)

    new_obj = {}

    for field in resource.fields:
        fields = None

        # this implies a nested relationship, but with explicitly defined
        # fields
        if type(field) is tuple:
            fields = field[1:]
            field = field[0]

        key = field
        if '->' in field:
            field, key = field.split('->')

        # only apply exclude to the first level since other depths need to
        # be explicitly defined
        if depth == 0 and field in resource.exclude:
            continue

        # test to see if the field is on the obj/model
        if hasattr(obj, field):
            value = getattr(obj, field)

        # fallback to a local resource method, pass in the object
        else:
            value = getattr(resource, field)(obj)

        # call if a callable
        if callable(value):
            value = value()

        # handle a local many-to-many or a reverse foreign key
        elif value.__class__.__name__ in ('RelatedManager', 'ManyRelatedManager'):
            value = value.all()

        new_obj[key] = convert_to_resource(value, fields=fields)

    return new_obj


def convert_to_resource(obj, *args, **kwargs):
    """Recursively attempts to find ``Model`` and ``QuerySet`` instances
    to convert them into their representative datastructure per their
    ``Resource`` (if one exists).
    """

    # handle model instances
    if isinstance(obj, models.Model):
        obj = model_to_resource(obj, *args, **kwargs)

    # handle querysets
    elif isinstance(obj, QuerySet):
        obj = queryset_to_resource(obj, *args, **kwargs)

    # handle dict instances
    elif isinstance(obj, dict):
        for k, v in obj.iteritems():
            obj[k] = convert_to_resource(v, *args, **kwargs)

    # handle other iterables
    elif hasattr(obj, '__iter__'):
        obj = [convert_to_resource(o, *args, **kwargs) for o in iter(obj)]

    return obj
