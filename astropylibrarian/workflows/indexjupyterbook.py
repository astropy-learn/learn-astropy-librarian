# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Workflow for ingesting a Jupyter Book site (as a Learn Astropy Guide).

This workflow ingests the Jupyter Book homepage and triggers workflows to
ingest individual Jupyter Book content pages.
"""

from __future__ import annotations

__all__ = ["index_jupyterbook"]

import asyncio
import logging
import re
from typing import TYPE_CHECKING, List, Union
from urllib.parse import urljoin

from astropylibrarian.algolia.client import generate_index_epoch
from astropylibrarian.reducers.jupyterbook import (
    JupyterBookMetadata,
    JupyterBookPage,
)
from astropylibrarian.workflows.download import download_html
from astropylibrarian.workflows.expirerecords import expire_old_records
from astropylibrarian.workflows.indexjupyterbookpage import (
    index_jupyterbook_page,
)

if TYPE_CHECKING:
    import aiohttp

    from astropylibrarian.client import AlgoliaIndexType
    from astropylibrarian.resources import HtmlPage

logger = logging.getLogger(__name__)


async def index_jupyterbook(
    *,
    url: str,
    http_client: aiohttp.ClientSession,
    algolia_index: AlgoliaIndexType,
    priority: int,
) -> List[str]:
    """Ingest a Jupyter Book site as a Learn Astropy Guide.

    Parameters
    ----------
    url : `str`
        A URL for an HTML page.
    http_client : `aiohttp.ClientSession`
        An open aiohttp client.
    algolia_index
        Algolia index created by the
        `astropylibrarian.workflows.client.AlgoliaIndex` context manager.
    priority : int
        A priority level that elevates a guide in the UI's default sorting.

    Returns
    -------
    object_ids : `list` of `str`
        List of Algolia record object IDs that are saved by this indexing
        operation.
    """
    homepage = await download_homepage(url=url, http_client=http_client)
    logger.debug("Downloaded %s", url)
    homepage_metadata = extract_homepage_metadata(
        html_page=homepage, root_url=url, priority=priority
    )
    logger.debug("Extracted JupyterBook metadata\n%s", homepage_metadata)
    page_urls = homepage_metadata.all_page_urls
    index_epoch = generate_index_epoch()
    tasks = [
        asyncio.create_task(
            index_jupyterbook_page(
                url=url,
                jupyterbook_metadata=homepage_metadata,
                index_epoch=index_epoch,
                algolia_index=algolia_index,
                http_client=http_client,
            )
        )
        for url in page_urls
    ]
    object_ids: List[str] = []
    for result in asyncio.as_completed(tasks):
        _objectids = await result
        object_ids.extend(_objectids)

    logger.info("Finished indexing JupyterBook %s (%d records)", url, len(object_ids))

    if object_ids:
        await expire_old_records(
            algolia_index=algolia_index,
            root_url=homepage_metadata.root_url,
            index_epoch=index_epoch,
        )

    return object_ids


async def download_homepage(
    *, url: str, http_client: "aiohttp.ClientSession"
) -> HtmlPage:
    """Download the HTML for the Jupyter Book's homepage, given the root
    URL

    This function solves the fact that the root URL hosts a redirect
    page

    Parameters
    ----------
    url : `str`
        The root URL of the Jupyter Book
    http_client : `aiohttp.ClientSession`
        An open aiohttp client.

    Returns
    -------
    astropylibrarian.resources.HtmlPage
        The HTML page.
    """
    index_page = await download_html(url=url, http_client=http_client)

    try:
        # Detect if the URL is a redirect to the true first content page
        redirect_url = detect_redirect(index_page)
        if isinstance(redirect_url, str):
            return await download_html(url=redirect_url, http_client=http_client)
    except Exception:
        pass

    return index_page


def detect_redirect(html_page: HtmlPage) -> Union[None, str]:
    """Detect if the page is actually an immediate redirect to another page
    via an "http-equiv=Refresh" meta tag.

    Parameters
    ----------
    html_page : `astropylibrarian.resources.HtmlPage`
        The HTML page.

    Returns
    -------
    `None` or `str`
        Returns `None` if the page is not a redirect. If the page *is* a,
        redirect, returns the URL of the target page.
    """
    doc = html_page.parse()
    # Now try to see if there is a <meta> tag with http-equiv="Refresh"
    for element in doc.cssselect("meta"):
        try:
            if element.attrib["http-equiv"].lower() == "refresh":
                return parse_redirect_url(
                    content=element.attrib["content"], source_url=html_page.url
                )
        except (KeyError, RuntimeError):
            continue

    return None


def parse_redirect_url(*, content: str, source_url: str) -> str:
    """Parse the http-equiv tag to create the redirect destination URL.

    Parameters
    ----------
    content : `str`
        The ``content`` attribute of the meta tag.
    source_url : `str`
        The URL of the page hosting the meta tag.

    Returns
    -------
    str
        The target URL of the redirection.

    Raises
    ------
    RuntimeError
        Raised if the content cannot be parsed.

    Examples
    --------
    >>> content = "0; url=notebooks/00-00-Preface.html"
    >>> source_url = "https://example.org/index.html"
    >>> parse_redirect_url(content=content, source_url=source_url)
    'https://example.org/notebooks/00-00-Preface.html'
    """
    m = re.match(r"\d+; url=(.+)", content)
    if m:
        redirect_path = m.group(1)
    else:
        raise RuntimeError("No url match")

    return urljoin(source_url, redirect_path)


def extract_homepage_metadata(
    *, html_page: HtmlPage, root_url: str, priority: int
) -> JupyterBookMetadata:
    """Extract JupyterBook project metadata from it's homepage.

    Parameters
    ----------
    html_page : astropylibrarian.resources.HtmlPage
        The downloaded JupyterBook homepage, see `download_homepage`.
    root_url : str
        The root URL of the JupyterBook. This value is typically the URL
        input to `index_jupyterbook` and becomes a unique identifier for all
        Algolia records related to a JupyterBook, across all of a JupyterBook's
        pages.
    priority : int
        A priority level that elevates a guide in the UI's default sorting.

    Returns
    -------
    JupyterBookMetadata
        Metadata associated with the JupyterBook project.
    """
    homepage = JupyterBookPage(html_page)
    md = JupyterBookMetadata(
        root_url=root_url,
        title=homepage.title,
        logo_url=homepage.logo_url,
        description=homepage.first_paragraph or "",
        source_repository=homepage.github_repository,
        homepage_url=homepage.url,
        page_urls=homepage.page_urls,
        priority=priority,
    )
    return md
