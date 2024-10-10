# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""The astropy-librarian crawls Astropy's web content and feeds its
search database.
"""

__all__ = ("__version__",)

try:
    from ._version import __version__ 
except ImportError:
    # package is not installed
    __version__ = ""
