# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Workflow for deleting old records."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from algoliasearch.search.models.browse_params_object import BrowseParamsObject

from astropylibrarian.algolia.client import escape_facet_value

if TYPE_CHECKING:
    from typing import List

    from astropylibrarian.algolia.client import AlgoliaIndexType

__all__ = ["expire_old_records"]

logger = logging.getLogger(__name__)


async def expire_old_records(
    *, algolia_index: AlgoliaIndexType, root_url: str, index_epoch: str
) -> List[str]:
    """Expire records for a root_url that do not match the index_epoch."""
    filters = (
        f"root_url:{escape_facet_value(root_url)}"
        " AND NOT "
        f"index_epoch:{escape_facet_value(index_epoch)}"
    )

    obj = BrowseParamsObject(
        filters=filters,
        attributes_to_retrieve=["root_url", "index_epoch"],
        attributes_to_highlight=[],
    )
    old_object_ids: List[str] = []
    # for r in await algolia_index.browse_objects(obj).hits:
    # records = await algolia_index.browse_objects(obj).hits
    response = await algolia_index.browse_objects(obj)
    records = response.hits
    for r in records:
        # Double check that we're deleting the right things.
        if r.root_url != root_url:
            logger.warning("root_url does not match: %s", r.root_url)
            continue
        if r.index_epoch == index_epoch:
            logger.warning("index_epoch matches current epoch: %s", r.index_epoch)
            continue
        old_object_ids.append(r.object_id)

    logger.info(
        "Collected %d old object_id for deletion, for %s",
        len(old_object_ids),
        root_url,
    )

    await algolia_index.delete_objects(old_object_ids)

    logger.info("Finished deleting expired objects for %s", root_url)

    return old_object_ids
