__title__ = 'puyu'
__author__ = 'staciax'
__license__ = 'MIT'
__copyright__ = 'Copyright 2025-present staciax'

import importlib.metadata

try:
    __version__ = importlib.metadata.version('puyu')
except importlib.metadata.PackageNotFoundError:
    # Fallback if running from source without being installed
    __version__ = '0.0.0'

del importlib
