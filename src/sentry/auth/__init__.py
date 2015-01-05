from __future__ import absolute_import, print_function

from .provider import *  # NOQA
from .manager import ProviderManager
from .view import *  # NOQA

providers = ProviderManager()
register = providers.register
unregister = providers.unregister
