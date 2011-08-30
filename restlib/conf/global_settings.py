# enables warnings which prints out messages at various locations. this should
# only be used for development. 
WARNINGS_ENABLED = False

# if any of the fields defined for a ModelResource class cannot be properly
# resolved for the model objects, by default, an AttributeError will be raised.
# setting this to ``True`` will ignore those errors. the missing fields will not
# be present in the output resolved object
IGNORE_MISSING_FIELDS = False

# the default representation when traversing related objects for any object. if
# this is set to ``True``, it will use the associated URI if a Resource has been
# defined for the related object's model. it it cannot determine the URI it will
# raise an AttributeError unless ``IGNORE_MISSING_FIELDS`` is ``True``
USE_HATEOAS_FOR_RELATED_OBJECTS = True

# the default set of middleware applied to all middleware. requests are processed
# from the top down, while responses are processed from the bottom up.
RESOURCE_MIDDLEWARE = (
    'restlib.resources.middleware.client.MethodNotAllowed',
    'restlib.resources.middleware.client.UnsupportedMediaType',
    'restlib.resources.middleware.client.UnprocessableEntity',
    'restlib.resources.middleware.client.NotAcceptable',
)
