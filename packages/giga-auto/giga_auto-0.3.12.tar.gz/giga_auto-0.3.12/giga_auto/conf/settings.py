import os
import importlib

class LazySettings(object):

    def __init__(self):
        self._settings = None

    def _set_business(self, name):
        if name == 'business':
            business_path = self._settings.business
            return importlib.import_module(business_path)
        return None

    def _set_assert_class(self, name):
        if name == 'assert_class':
            if getattr(self._settings,name,None) is not None:
                assert_class_path = self._settings.assert_class
            else:
                assert_class_path = 'giga_auto.assert_utils.AssertUtils'
            module,class_obj=assert_class_path.rsplit('.',1)
            return getattr(importlib.import_module(module), class_obj)
        return None

    def _set_main(self, name):
        return (self._set_business(name)
                or self._set_assert_class(name)
                or getattr(self._settings, name))
    def __getattr__(self, name):
        if self._settings is None:
            module_path = os.environ['GIGA_SETTINGS_MODULE']
            self._settings = importlib.import_module(module_path)
        return self._set_main(name)


settings = LazySettings()
