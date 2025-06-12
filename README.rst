#######################
learn-astropy-librarian
#######################

The content crawler that supplies Learn Astropy's web search.

Command line interface
======================

::

    Usage: astropylibrarian [OPTIONS] COMMAND [ARGS]...

      Manage the content index for the Learn Astropy project.

      Astropy Librarian helps you work with the Algolia index that powers the
      content listing and search for Learn Astropy, https://learn.astropy.org.

      Astropy Librarian is developed at https://github.com/astropy-learn/learn-
      astropy-librarian

    Options:
      -v, --verbose                   Verbose output. Use -v for info-type logging
                                      and -vv for debug-level logging.  [default:
                                      0]

      --install-completion [bash|zsh|fish|powershell|pwsh]
                                      Install completion for the specified shell.
      --show-completion [bash|zsh|fish|powershell|pwsh]
                                      Show completion for the specified shell, to
                                      copy it or customize the installation.

      --help                          Show this message and exit.

    Commands:
      delete  Delete Algolia records.
      index   Content indexing commands.

astropylibrarian index tutorial
-------------------------------

::

    Usage: astropylibrarian index tutorial [OPTIONS] URL

      Index a single tutorial.

    Arguments:
      URL  URL for a tutorial.  [required]

    Options:
      --algolia-id TEXT   Algolia app ID.  [env var: ALGOLIA_ID; required]
      --algolia-key TEXT  Algolia API key.  [env var: ALGOLIA_KEY; required]
      --index TEXT        Name of the Algolia index.  [env var: ALGOLIA_INDEX;
                          required]

      --priority INTEGER  Priority for default sorting (higher numbers appear
                          first)  [default: 0]

      --path PATH         Local path of tutorial HTML, if available.
      --help              Show this message and exit.

astropylibrarian index tutorial-site
------------------------------------


::

  Usage: astropylibrarian index tutorial-site [OPTIONS] SITE_DIR URL

    Index a directory of tutorial HTML files.

    This command is useful for automated CI workflows. The site_dir argument
    is the directory of tutorials built by nbcollection and url is the root
    URL where these tutorials are published on the web. This command indexes
    each HTML file as a tutorial, except for those with paths specified in the
    --ignore argument. The root index.html file is always ignored.

  Arguments:
    SITE_DIR  Local path tutorial build directory  [required]
    URL       Base URL for tutorials.  [required]

  Options:
    --algolia-id TEXT   Algolia app ID.  [env var: ALGOLIA_ID; required]
    --algolia-key TEXT  Algolia API key.  [env var: ALGOLIA_KEY; required]
    --index TEXT        Name of the Algolia index.  [env var: ALGOLIA_INDEX;
                        required]

    --ignore TEXT       List of HTML files to ignore from indexing. The root
                        index.html file is always excluded.  [default:
                        (dynamic)]

    --help              Show this message and exit.

astropylibrarian index guide
----------------------------

::

    Usage: astropylibrarian index guide [OPTIONS] URL

      Index a guide.

    Arguments:
      URL  Root URL for a guide.  [required]

    Options:
      --algolia-id TEXT   Algolia app ID.  [env var: ALGOLIA_ID; required]
      --algolia-key TEXT  Algolia API key.  [env var: ALGOLIA_KEY; required]
      --index TEXT        Name of the Algolia index.  [env var: ALGOLIA_INDEX;
                          required]

      --priority INTEGER  Priority for default sorting (higher numbers appear
                          first)  [default: 0]

      --help              Show this message and exit.

astropylibrarian delete
-----------------------

::

    Usage: astropylibrarian delete [OPTIONS] URL

      Delete Algolia records.

    Arguments:
      URL  Root URL to delete  [required]

    Options:
      --algolia-id TEXT   Algolia app ID.  [env var: ALGOLIA_ID; required]
      --algolia-key TEXT  Algolia API key.  [env var: ALGOLIA_KEY; required]
      --index TEXT        Name of the Algolia index.  [env var: ALGOLIA_INDEX;
                          required]

      --help              Show this message and exit.

Development primer
==================

Before developing learn-astropy-librarian, set up a new Python virtual environment.
Then, install the application with development dependencies::

    make init

This command installs pre-commit hooks for code linting, installs tox, resets the tox environment, and installs the package itself.

You can run all tests through tox_::

    tox

You can also run tox environments individually:

- ``tox -e py`` runs unit tests with Pytest_.
- ``tox -e lint`` runs code linters (such as flake8_ and pre-commit_).
- ``tox -e typing`` runs mypy_ to check type annotations.

.. _Pytest: https://pytest.org/en/latest/
.. _mypy: https://mypy.readthedocs.io/en/latest/
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _pre-commit: https://pre-commit.com
