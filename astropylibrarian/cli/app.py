# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Command-line interface for astropylibrarian."""

from __future__ import annotations

import asyncio
import logging

import typer

from astropylibrarian.algolia.client import AlgoliaIndex
from astropylibrarian.cli import index
from astropylibrarian.workflows.deleterooturl import delete_root_url

app = typer.Typer(short_help="Manage the content indexed by the Learn Astropy project.")
app.add_typer(index.app, name="index")


@app.callback()
def main_callback(
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help=(
            "Verbose output. Use -v for info-type logging and -vv for "
            "debug-level logging."
        ),
    ),
) -> None:
    """Manage the content index for the Learn Astropy project.

    Astropy Librarian helps you work with the Algolia index that powers
    the content listing and search for Learn Astropy,
    https://learn.astropy.org.

    Astropy Librarian is developed at
    https://github.com/astropy-learn/learn-astropy-librarian
    """
    if verbose == 0:
        logging_level = logging.WARN
    elif verbose == 1:
        logging_level = logging.INFO
    else:
        logging_level = logging.DEBUG

    if logging_level == logging.DEBUG:
        # Include the module name in the logging for easier debugging
        log_format = "%(asctime)s %(levelname)8s %(name)s:%(lineno)d | %(message)s"
    else:
        log_format = "%(levelname)s: %(message)s"

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format, datefmt="%Y-%m-%d:%H:%M:%S"))
    logger = logging.getLogger("astropylibrarian")
    logger.addHandler(handler)
    logger.setLevel(logging_level)


@app.command()
def delete(
    url: str = typer.Argument(..., help="Root URL to delete"),
    algolia_id: str = typer.Option(..., help="Algolia app ID.", envvar="ALGOLIA_ID"),
    algolia_key: str = typer.Option(
        ...,
        help="Algolia API key.",
        envvar="ALGOLIA_KEY",
        prompt=True,
        confirmation_prompt=False,
        hide_input=True,
    ),
    index: str = typer.Option(
        ..., help="Name of the Algolia index.", envvar="ALGOLIA_INDEX"
    ),
) -> None:
    """Delete Algolia records."""
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(
        run_delete(
            url=url,
            algolia_id=algolia_id,
            algolia_key=algolia_key,
            index=index,
        )
    )


async def run_delete(
    *, url: str, algolia_id: str, algolia_key: str, index: str
) -> None:
    async with AlgoliaIndex(
        key=algolia_key, app_id=algolia_id, name=index
    ) as algolia_index:
        await delete_root_url(root_url=url, algolia_index=algolia_index)


@app.command()
def clear_index(
    algolia_id: str = typer.Option(..., help="Algolia app ID.", envvar="ALGOLIA_ID"),
    algolia_key: str = typer.Option(
        ...,
        help="Algolia API key.",
        envvar="ALGOLIA_KEY",
        prompt=True,
        confirmation_prompt=False,
        hide_input=True,
    ),
    index: str = typer.Option(
        ..., help="Name of the Algolia index.", envvar="ALGOLIA_INDEX"
    ),
) -> None:
    """
    Clear all records from an Algolia index without deleting the index itself.
    This removes all records in the index but retains the index configuration.
    """
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(
        run_clear_index(
            algolia_id=algolia_id,
            algolia_key=algolia_key,
            index=index,
        )
    )

async def run_clear_index(*, algolia_id: str, algolia_key: str, index: str) -> None:
    async with AlgoliaIndex(
        key=algolia_key, app_id=algolia_id, name=index
    ) as algolia_index:    
        await algolia_index.clear_objects()

if __name__ == "__main__":
    app()