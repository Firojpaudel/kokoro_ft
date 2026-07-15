try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # For Python <3.8

try:
    __version__ = version("monotonic_align")
except Exception:
    __version__ = "0.0.0"

from monotonic_align.mas import *
