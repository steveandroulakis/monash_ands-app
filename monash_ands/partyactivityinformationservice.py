'''
Publish Service (for working with PublishProvider instances)

.. moduleauthor:: Steve Androulakis <steve.androulakis@monash.edu>
'''
from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)

from django.conf import settings

class PartyActivityInformationService():

    def __init__(self):
        self._pai_provider = None
        self._initialised = False

        import sys
        self.settings = sys.modules['%s.%s.settings' %
                    (settings.TARDIS_APP_ROOT, 'monash_ands')]

    def _manual_init(self):
        """Manual init had to be called by all the functions of the PublishService
        class to initialise the instance variables. This block of code used to
        be in the __init__ function but has been moved to its own init function
        to get around the problems with cyclic imports to static variables
        being exported from auth related modules.

        """
        self._pai_provider = self._safe_import(self.settings.PARTY_ACTIVITY_INFORMATION_PROVIDER)
        self._initialised = True

    def _safe_import(self, path):
        try:
            dot = path.rindex('.')
        except ValueError:
            raise ImproperlyConfigured(\
                '%s isn\'t a middleware module' % path)
        pai_module, pai_classname = path[:dot], path[dot + 1:]
        try:
            mod = import_module(pai_module)
        except ImportError, e:
            raise ImproperlyConfigured(\
                'Error importing Party Activity Information module %s: "%s" \
                    ' %
                                       (pai_module, e))
        try:
            pai_class = getattr(mod, pai_classname)
        except AttributeError:
            raise ImproperlyConfigured(\
                'Party Activity Information module "%s" does not define a" \
                    "%s" class' %
                                       (pai_module, pai_classname))

        pai_instance = pai_class()
        return pai_instance

    def get_pai(self):
        """Return a list Party Activity Information providers

        """
        if not self._initialised:
            self._manual_init()

        return self._pai_provider
