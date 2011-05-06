from django.utils.functional import LazyObject
from django.conf import settings as all_settings

from restlib.conf import global_settings

class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings(all_settings.__dict__)


class Settings(object):
    def __init__(self, settings_dict):
        # set default settings up front
        for setting in dir(global_settings):
            if setting != setting.upper():
                continue

            if setting in settings_dict:
                value = settings_dict[setting]
            else:
                value = getattr(global_settings, setting)
            setattr(self, setting, value)


settings = LazySettings()
