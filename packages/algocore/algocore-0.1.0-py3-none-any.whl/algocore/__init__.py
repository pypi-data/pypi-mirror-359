from importlib.metadata import metadata

try:
    _metadata = metadata("algocore")
    __version__ = _metadata["Version"]
    __author__ = _metadata["Author"]
    __maintainer__ = _metadata["Maintainer"]
except Exception:  # noqa: BLE001
    __version__ = "unknown"
    __author__ = "Ben Elfner"
    __maintainer__ = "Ben Elfner"

from .decorators import *
from .functions import *
from .utils import *
