import imp

from django.conf import settings
from django.utils.importlib import import_module

from restlib.resources.base import *
from restlib.resources.model import *

LOADING = False
RESOURCE_MODULE_NAME = 'resources'

def autodiscover():
    global LOADING

    if LOADING:
        return

    LOADING = True

    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue
        try:
            imp.find_module(RESOURCE_MODULE_NAME, app_path)
        except ImportError:
            continue

        import_module('%s.%s' % (app, RESOURCE_MODULE_NAME))

    LOADING = False
