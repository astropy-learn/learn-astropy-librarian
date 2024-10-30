# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Workflow for ingesting a single page from a Jupyter Book site"""

from __future__ import annotations

__all__ = ["index_jupyterbook_page"]

import logging
from typing import TYPE_CHECKING, List

from astropylibrarian.reducers.jupyterbook import JupyterBookPage
from astropylibrarian.workflows.download import download_html

if TYPE_CHECKING:
    import aiohttp

    from astropylibrarian.client import AlgoliaIndexType
    from astropylibrarian.workflows.indexjupyterbook import JupyterBookMetadata

logger = logging.getLogger(__name__)


async def index_jupyterbook_page(
    *,
    url: str,
    jupyterbook_metadata: JupyterBookMetadata,
    http_client: aiohttp.ClientSession,
    algolia_index: AlgoliaIndexType,
    index_epoch: str,
) -> List[str]:
    """Ingest a page from a JupyterBook site."""
    html_page = await download_html(url=url, http_client=http_client)
    logger.debug("Downloaded %s", url)

    page = JupyterBookPage(html_page)
    records = [
        record
        for record in page.iter_algolia_objects(
            site_metadata=jupyterbook_metadata, index_epoch=index_epoch
        )
    ]
    logger.debug(
        "Indexing %d records for Jupyter Book page at %s", len(records), url
    )
    response = await algolia_index.save_objects(index_name="", objects=records)
    logger.debug("Algolia save_objects: %s", response.raw_responses)

    object_ids = [r["objectID"] for r in records]

    logger.info(
        "Finished indexing JupyterBook page: %s (%d records)",
        url,
        len(object_ids),
    )
    return object_ids
