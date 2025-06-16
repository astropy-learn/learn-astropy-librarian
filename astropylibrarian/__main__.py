# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""This module enables running the CLI as::

python -m astropylibrarian
"""

from astropylibrarian.cli.app import app

if __name__ == "__main__":
    app(prog_name="astropylibrarian")
