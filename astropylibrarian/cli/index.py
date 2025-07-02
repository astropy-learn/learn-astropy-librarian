# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Astropy Librarian CLI "index" subcommand group."""

from __future__ import annotations

import asyncio
from pathlib import Path, PosixPath
from typing import Awaitable, List, Optional

import aiohttp
import fnmatch
import typer

from astropylibrarian.algolia.client import AlgoliaIndex
from astropylibrarian.workflows.indexjupyterbook import index_jupyterbook
from astropylibrarian.workflows.indextutorial import (
    index_tutorial_from_path,
    index_tutorial_from_url,
)

app = typer.Typer(short_help="Content indexing commands.")


@app.command()
def tutorial(
    url: str = typer.Argument(..., help="URL or path for a tutorial."),
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
    priority: int = typer.Option(
        0,
        help="Priority for default sorting (higher numbers appear first)",
    ),
    path: Optional[Path] = typer.Option(
        None, help="Local path of tutorial HTML, if available."
    ),
) -> None:
    """Index a single tutorial."""
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(
        run_index_tutorial(
            url=url,
            algolia_id=algolia_id,
            algolia_key=algolia_key,
            index=index,
            priority=priority,
            path=path,
        )
    )


@app.command("tutorial-site")
def tutorial_site(
    site_dir: Path = typer.Argument(..., help="Local path tutorial build directory"),
    url: str = typer.Argument(..., help="Base URL for tutorials."),
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
    ignore: List[str] = typer.Option(
        lambda: ["index.html"],
        help=(
            "List of HTML files to ignore from indexing. The root index.html "
            "file is always excluded."
        ),
    ),
) -> None:
    """Index a directory of tutorial HTML files.

    This command is useful for automated CI workflows. The site_dir argument
    is the directory of tutorials built by nbcollection and url is the root
    URL where these tutorials are published on the web. This command indexes
    each HTML file as a tutorial, except for those with paths specified in
    the --ignore argument. The root index.html file is always ignored.
    """
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(
        run_index_tutorial_site(
            site_dir=site_dir,
            root_url=url,
            algolia_id=algolia_id,
            algolia_key=algolia_key,
            index=index,
            ignore_paths=ignore,
        )
    )


async def run_index_tutorial_site(
    *,
    site_dir: Path,
    root_url: str,
    algolia_id: str,
    algolia_key: str,
    index: str,
    ignore_paths: List[str],
) -> None:
    # For consistency when building page urls
    if root_url.endswith("/"):
        root_url.rstrip("/")

    async with aiohttp.ClientSession() as http_client:
        async with AlgoliaIndex(
            key=algolia_key, app_id=algolia_id, name=index
        ) as algolia_index:
            site_dir.resolve()
            html_paths = site_dir.glob("**/*.html")
            tasks: List[Awaitable] = []
            for html_path in html_paths:
                relative_path = str(PosixPath(html_path.relative_to(site_dir)))
                if relative_path in ignore_paths:
                    continue
                # allow wildcard matching with ignore_paths
                if fnmatch.fnmatch(relative_path, ignore_paths):
                    continue
                page_url = f"{root_url}/{relative_path}"
                tasks.append(
                    index_tutorial_from_path(
                        path=html_path,
                        url=page_url,
                        http_client=http_client,
                        algolia_index=algolia_index,
                        # hard-coded for now, will add a config system later
                        priority=0,
                    )
                )
            await asyncio.gather(*tasks)


async def run_index_tutorial(
    *,
    url: str,
    algolia_id: str,
    algolia_key: str,
    index: str,
    priority: int,
    path: Optional[Path] = None,
) -> None:
    async with aiohttp.ClientSession() as http_client:
        async with AlgoliaIndex(
            key=algolia_key, app_id=algolia_id, name=index
        ) as algolia_index:
            if path:
                await index_tutorial_from_path(
                    path=path,
                    url=url,
                    http_client=http_client,
                    algolia_index=algolia_index,
                    priority=priority,
                )
            else:
                await index_tutorial_from_url(
                    url=url,
                    http_client=http_client,
                    algolia_index=algolia_index,
                    priority=priority,
                )


@app.command()
def guide(
    url: str = typer.Argument(..., help="Root URL for a guide."),
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
    priority: int = typer.Option(
        0,
        help="Priority for default sorting (higher numbers appear first)",
    ),
) -> None:
    """Index a guide."""
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(
        run_index_guide(
            url=url,
            algolia_id=algolia_id,
            algolia_key=algolia_key,
            index=index,
            priority=priority,
        )
    )


async def run_index_guide(
    *, url: str, algolia_id: str, algolia_key: str, index: str, priority: int
) -> None:
    async with aiohttp.ClientSession() as http_client:
        async with AlgoliaIndex(
            key=algolia_key, app_id=algolia_id, name=index
        ) as algolia_index:
            await index_jupyterbook(
                url=url,
                http_client=http_client,
                algolia_index=algolia_index,
                priority=priority,
            )
