# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Record types that reflect Algolia search records."""

from __future__ import annotations

__all__ = ["ContentType", "AlgoliaRecord", "TutorialRecord", "GuideRecord"]

import copy
import datetime
import json
import math
import re
from base64 import b64encode
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional
from urllib.parse import urlparse, urlunparse

from more_itertools import chunked
from pydantic.v1 import UUID4, BaseModel, Field, HttpUrl, validator

if TYPE_CHECKING:
    from astropylibrarian.keywords import KeywordDb
    from astropylibrarian.reducers.jupyterbook import (
        JupyterBookMetadata,
        JupyterBookPage,
    )
    from astropylibrarian.reducers.tutorial import ReducedTutorial
    from astropylibrarian.reducers.utils import Section


class ContentType(str, Enum):
    """Learn Astropy content types."""

    tutorial = "tutorial"

    guide = "guide"

    example = "example"

    documentation = "documentation"


class AlgoliaRecord(BaseModel):
    """A Pydantic model for a Learn Astropy record in Algolia."""

    objectID: str = Field(description="Unique identifier for this record.")

    index_epoch: UUID4 = Field(
        description=(
            "Indexing epoch for this root_url. All records with the same "
            "root_url are ingested at the same time using the same "
            "index_epoch value. This enables old records, with a "
            "different index_epoch value to be deleted."
        )
    )

    root_summary: Optional[str] = Field(
        description=("Short summary of the content corresponding to the root_url.")
    )

    content_type: ContentType = Field(description="Content type.")

    url: HttpUrl = Field(
        description=(
            "The most-specific URL for this record. Compared to the base url "
            "this URL may contain things like fragments in the URL."
        ),
    )

    root_url: HttpUrl = Field(
        description=(
            "URL of the document project's root page. For multi-page sites "
            "this corresponds to the site's homepage. For single-page sites "
            "this corresponds to the page's URL and is the same as "
            "``baseUrl``."
        ),
    )

    root_title: str = Field(
        description=(
            "Title of the documentation project. For single-page sites "
            "This is the same as ``h1``."
        ),
    )

    base_url: HttpUrl = Field(
        description=(
            "The base URL of the page, without fragments, parameters, queries, etc."
        ),
    )

    h1: str = Field(description="The title.")

    h2: Optional[str] = Field(description="The second-level heading.")

    h3: Optional[str] = Field(description="The third-level heading.")

    h4: Optional[str] = Field(description="The fourth-level heading.")

    h5: Optional[str] = Field(description="The fifth-level heading.")

    h6: Optional[str] = Field(description="The sixth-level heading.")

    importance: int = Field(
        description="The importance of the record, corresponding to the "
        "hierarchical section level"
    )

    content: str = Field(description="The plain text content of the record.")

    date_indexed: datetime.datetime = Field(
        description="Timestamp when the record was indexed.",
        default_factory=datetime.datetime.utcnow,
    )

    thumbnail_url: Optional[HttpUrl] = Field(
        description="URL of an image to use as a thumbnail.",
    )

    priority: int = Field(
        0,
        description="Higher values of priority are sorted higher in the "
        "default search (before a user enters a search term).",
    )

    @staticmethod
    def compute_object_id_for_section(section: Section) -> str:
        """Compute an Algolia ``objectID`` given a content section.

        Parameters
        ----------
        section : `astropylibrarian.reducers.utils.Section`
            A content section.

        Returns
        -------
        str
            The ``objectID`` for an Algolia record.
        """
        url_component = b64encode(section.url.lower().encode("utf-8")).decode("utf-8")
        heading_component = b64encode(
            " ".join(section.headings).encode("utf-8")
        ).decode("utf-8")
        return f"{url_component}-{heading_component}"

    def export_to_algolia(self) -> Dict[str, Any]:
        """Export this model into an object that can be uploaded with the
        Algolia client.

        For a method that yields records to fit inside Algolia record size
        caps, see `export_capped_records_to_algolia`.

        Notes
        -----
        This method:

        1. Serializes to JSON so that all types are JSON-compatible. It also
           applies the exclude_none argument to pydantic ``BaseModel.json``
           method.
        2. Deserializes the JSON into a dict
        """
        json_data = self.json(exclude_none=True)
        return json.loads(json_data)

    def export_capped_records_to_algolia(
        self, max_size: int = 9500
    ) -> Iterator[Dict[str, Any]]:
        """Yield objects for upload to Algolia from this record that each
        fit within the Algolia size cap for an individual record.

        Parameters
        ----------
        max_size : int
            The maximum record size, in bytes.

        Yields
        ------
        algolia_record : dict
            An individual Algolia object derived from this record (see
            `export_to_algolia`). If the entire record can fit within the size
            cap, that is the only record yield. Otherwise, the ``content`` is
            split across multiple sub-records that fit within the size cap.
            Each sub-record has an integer suffix added to the ``objectID``.
        """
        json_record = self.export_to_algolia()
        total_bytes = len(json.dumps(json_record).encode("utf-8"))

        if total_bytes < max_size:
            yield json_record

        else:
            # split content by sentences.
            content_chunks = re.split(r"\. ", self.content)
            split_by = math.ceil(total_bytes / max_size)
            part_size = math.floor(len(content_chunks) / split_by)
            for i, chunk in enumerate(chunked(content_chunks, part_size), 1):
                sub_record = copy.deepcopy(self)
                sub_record.content = ". ".join(chunk)
                # patch the object ID with a chunk number suffix
                sub_record.objectID = f"{self.objectID}-{i}"
                yield sub_record.export_to_algolia()

    def split(self, number: int) -> List[AlgoliaRecord]:
        """Split a record in a given number of parts; evenly distributing
        the content between parts.
        """
        p = re.compile(r"\. ")
        content_chunks = p.split(self.content)
        part_size = math.floor(len(content_chunks) / number)
        split_records: List[AlgoliaRecord] = []
        for i, chunk in enumerate(chunked(content_chunks, part_size), 1):
            new_record = copy.deepcopy(self)
            new_record.content = ". ".join(chunk)
            # patch the object ID with a chunk number suffix
            new_record.objectID = f"{self.objectID}-{i}"
            split_records.append(new_record)
        return split_records


class TutorialRecord(AlgoliaRecord):
    """A Pydantic model for a "tutorial" content type record."""

    authors: Optional[List[str]] = Field(description="List of author names.")

    astropy_package_keywords: Optional[List[str]] = Field(
        description="List of astropy package keywords.",
    )

    python_package_keywords: Optional[List[str]] = Field(
        description="List of python package keywords.",
    )

    task_keywords: Optional[List[str]] = Field(description="List of task keywords.")

    science_keywords: Optional[List[str]] = Field(
        description="List of science keywords."
    )

    content_type: ContentType = Field(
        description="Content type.", default=ContentType.tutorial
    )

    @validator("content_type")
    def validate_content_type(cls, v: Optional[str]) -> str:
        if v is None:
            return ContentType.tutorial
        elif v != ContentType.tutorial:
            raise ValueError("Content type must be `tutorial`.")
        return v

    @classmethod
    def from_section(
        cls,
        *,
        tutorial: ReducedTutorial,
        section: Section,
        keyworddb: KeywordDb,
        index_epoch: str,
        priority: int,
    ) -> TutorialRecord:
        """Create a TutorialRecord from a reduced tutorial HTML page and
        specific section.

        Parameters
        ----------
        tutorial : astropylibrarian.reducers.tutorial.ReducedTutorial
            The tutorial.
        section : astropylibrarian.reducers.utils.Section
            A section of the tutorial, which corresponds 1:1 with an Algolia
            record.
        keyworddb : astropylibrarian.keywords.KeywordDb
            The keyword database to sort keywords in tutorials into
            categories for the Learn Astropy UI.
        index_epoch
            A unique identifier for the indexing run.
        priority : int
            A priority level that elevates a tutorial in the UI's default
            sorting.

        Returns
        -------
        TutorialRecord
            A tutorial record, ready to index in Algolia.
        """
        base_url = cls.compute_base_url(tutorial=tutorial)
        kwargs: Dict[str, Any] = {
            "objectID": cls.compute_object_id_for_section(section),
            "index_epoch": index_epoch,
            "url": section.url,
            "root_url": base_url,
            "root_title": tutorial.h1,
            "root_summary": tutorial.summary,
            "base_url": base_url,
            "importance": section.header_level,
            "content": section.content,
            "authors": tutorial.authors,
            "astropy_package_keywords": keyworddb.filter_keywords(
                tutorial.keywords, "astropy_package"
            ),
            "python_package_keywords": keyworddb.filter_keywords(
                tutorial.keywords, "python_package"
            ),
            "task_keywords": keyworddb.filter_keywords(tutorial.keywords, "task"),
            "science_keywords": keyworddb.filter_keywords(tutorial.keywords, "science"),
            "priority": priority,
        }
        for i, heading in enumerate(section.headings):
            kwargs[f"h{i + 1}"] = heading
        if tutorial.images:
            # TODO consider an explicitly set thumbnail from tutorial metadata
            kwargs["thumbnail_url"] = tutorial.images[0]

        return cls(**kwargs)

    @staticmethod
    def compute_base_url(*, tutorial: ReducedTutorial) -> str:
        """The base URL of the tutorial that the section belongs to.

        This is the section's ``url`` attribute stripped of the fragment
        (``#id`` part).
        """
        url_parts = urlparse(tutorial.url)
        return urlunparse(
            (url_parts.scheme, url_parts.netloc, url_parts.path, "", "", "")
        )


class GuideRecord(AlgoliaRecord):
    """A Pydantic model of a "guide" content type record."""

    content_type: ContentType = Field(
        description="Content type.", default=ContentType.guide
    )

    @validator("content_type")
    def validate_content_type(cls, v: Optional[str]) -> str:
        if v is None:
            return ContentType.guide
        elif v != ContentType.guide:
            raise ValueError("Content type must be `guide`.")
        return v

    @classmethod
    def from_section(
        cls,
        *,
        site_metadata: JupyterBookMetadata,
        page: JupyterBookPage,
        section: Section,
        index_epoch: str,
    ) -> GuideRecord:
        if page.image_urls:
            # TODO consider getting a thumbnail explicitly set form guide
            # metadata
            thumbnail_url: Optional[str] = page.image_urls[0]
        elif site_metadata.logo_url:
            thumbnail_url = site_metadata.logo_url
        else:
            thumbnail_url = None

        # The importance of 1 is reserved for the homepage URL so that the
        # homepage is featured in default listings. All other records have
        # importance bumped down lower.
        if (page.url == site_metadata.homepage_url) and (section.header_level == 1):
            importance = 1
        else:
            importance = section.header_level + 1

        kwargs: Dict[str, Any] = {
            "objectID": cls.compute_object_id_for_section(section),
            "index_epoch": index_epoch,
            "url": section.url,
            "root_url": site_metadata.root_url,
            "root_title": site_metadata.title,
            "root_summary": site_metadata.description,
            "base_url": page.url,
            "importance": importance,
            "content": section.content,
            "thumbnail_url": thumbnail_url,
            "priority": site_metadata.priority,
        }
        for i, heading in enumerate(section.headings):
            kwargs[f"h{i + 1}"] = heading
        return cls(**kwargs)
