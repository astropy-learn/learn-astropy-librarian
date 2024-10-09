# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""The astropy-librarian crawls Astropy's web content and feeds its
search database.
"""

__all__ = ("__version__",)

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"
