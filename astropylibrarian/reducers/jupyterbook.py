# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Reduce the HTML source of a JupyterBook-based Guide into search records."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional
from urllib.parse import urljoin, urlparse, urlunparse

from pydantic.v1 import BaseModel, HttpUrl, validator

from astropylibrarian.algolia.records import GuideRecord
from astropylibrarian.reducers.utils import iter_sphinx_sections

from logging import getLogger
logger = getLogger(__name__)

if TYPE_CHECKING:
    import lxml.html

    from astropylibrarian.reducers.utils import Section
    from astropylibrarian.resources import HtmlPage


class JupyterBookPage:
    """A JupyterBook page, with accessors to key content."""

    def __init__(self, html_page: HtmlPage):
        self.html_page = html_page
        self._doc = self.html_page.parse()

    @property
    def doc(self) -> lxml.html.HtmlElement:
        return self._doc

    @property
    def url(self) -> str:
        return self.html_page.url

    @property
    def title(self) -> Optional[str]:
        """The site's title (selector: ``#site-title``)."""
        try:
            element = self.doc.cssselect("#site-title")[0]
        except IndexError:
            return None
        return element.text_content()

    @property
    def logo_url(self) -> Optional[str]:
        """The URL of the site's logo (selector: ``img.logo``)."""
        try:
            element = self.doc.cssselect("img.logo")[0]
        except IndexError:
            return None
        return urljoin(self.html_page.url, element.attrib["src"])

    @property
    def first_paragraph(self) -> Optional[str]:
        """The content of the first paragraph within the main content
        (``#main-content``).
        """
        try:
            first_paragraph = self.doc.cssselect("#main-content p")[0]
        except IndexError:
            return None
        content = first_paragraph.text_content()
        return self._clean_content(content)

    @property
    def github_repository(self) -> Optional[str]:
        """The GitHub repository URL, detected in the ``<nav>`` element."""
        elements = self.doc.cssselect("nav a.external")
        for element in elements:
            href = element.attrib["href"]
            if href.startswith("https://github.com"):
                return href

        return None

    @property
    def page_urls(self) -> List[str]:
        """URLs of all pages in a JupyterBook, selected from the ``<nav>``
        with ID ``bd-docs-nav``.
        """
        return [
            urljoin(self.html_page.url, link.attrib["href"])
            for link in self.doc.cssselect("nav#bd-docs-nav a.internal")
            if link.attrib["href"] != "#"  # skip homepage
        ]

    @property
    def image_urls(self) -> List[str]:
        """URLs to images in the main content area."""
        images = self.doc.cssselect("#main-content img")
        return [urljoin(self.url, img.attrib["src"]) for img in images]

    def iter_sections(self) -> Iterator[Section]:
        """Iterate through sections in the page.

        Yields
        ------
        astropylibrarian.reducers.utils.Section
            A section of the document, which includes its content, heading
            hierarchy and anchor link.
        """
        # Try multiple selectors to find the main content
        selectors = [
            "#main-content .section",
            "#main-content",
            ".main-content .section",
            ".main-content",
            "main .section",
            "main",
            ".section",
            "article",
        ]        
        
        # root = self.doc.cssselect("#main-content .section")[0]
        root = None
        for selector in selectors:
            elements = self.doc.cssselect(selector)
            if elements:
                root = elements[0]
                logger.debug(f"Found content using selector: {selector} for {self.html_page.url}")
                break

        if root is None:
            logger.warning(
                f"Could not find any content sections for {self.html_page.url}. "
                f"Tried selectors: {selectors}. Skipping this page."
            )
            return
    
        for section in iter_sphinx_sections(
            root_section=root,
            base_url=self.html_page.url,
            headers=[],
            header_callback=lambda x: x.rstrip("¶"),
            content_callback=self._clean_content,
        ):
            yield section

    def iter_records(
        self, *, site_metadata: JupyterBookMetadata, index_epoch: str
    ) -> Iterator[GuideRecord]:
        """Iterate over all Algolia search database records that are
        extractable from the page.

        Parameters
        ----------
        site_metadata : `JupyterBookMetadata`
            Metadata about the JupyterBook site, as a whole. This information
            is included with each
            `~astropylibrarian.algolia.records.GuideRecord` to provide
            context for the search record within a guide..
        index_epoch : str
            A unique identifier for the indexing job. This is used to delete
            old records from previous indexings.

        Yields
        ------
        `astropylibrarian.algolia.records.GuideRecord`
            A record that is exportable to Algolia.
        """
        for section in self.iter_sections():
            yield GuideRecord.from_section(
                site_metadata=site_metadata,
                page=self,
                section=section,
                index_epoch=index_epoch,
            )

    def iter_algolia_objects(
        self, *, site_metadata: JupyterBookMetadata, index_epoch: str
    ) -> Iterator[Dict[str, Any]]:
        """Iterate over all objects that are extractable from the page in
        a format ready to use with the algoliasearch client.

        Parameters
        ----------
        site_metadata : `JupyterBookMetadata`
            Metadata about the JupyterBook site, as a whole. This information
            is included with each
            `~astropylibrarian.algolia.records.GuideRecord` to provide
            context for the search record within a guide..
        index_epoch : str
            A unique identifier for the indexing job. This is used to delete
            old records from previous indexings.

        Yields
        ------
        `dict`
            An object compatible with algolia search ``save_objects``-type
            methods.
        """
        for record in self.iter_records(
            site_metadata=site_metadata, index_epoch=index_epoch
        ):
            yield record.export_to_algolia()

    @staticmethod
    def _clean_content(x: str) -> str:
        """Clean HTML content by removing extra newlines."""
        x = x.replace(r"\n", " ")
        x = x.replace("\n", " ")
        x = x.replace("\\", " ")
        x = x.strip()
        return x


class JupyterBookMetadata(BaseModel):
    """Metadata for a JupyterBook project.

    This metadata can be associated with individual page in a JupyterBook
    to give that page context.
    """

    root_url: HttpUrl
    """Root URL of the JupyterBook.

    The URL is validated to guarantee than it ends with a "/".
    """

    title: str
    """The title of the JupyterBook as a plain text string."""

    logo_url: HttpUrl
    """The URL of the JupyterBook's logo."""

    description: str
    """The description of the JupyterBook, extracted as the first content
    paragraph of the book.

    This string is unformatted (no HTML formatting).
    """

    source_repository: Optional[HttpUrl]
    """The URL of the book's source repository (i.e. GitHub repository)."""

    homepage_url: HttpUrl
    """The URL of the homepage.

    This is not necessarily the same as the root_url, which redirects to this
    homepage_url.
    """

    page_urls: List[HttpUrl]
    """URLs of pages in the JupyterBook."""

    priority: int
    """A priority level that elevates a guide in the UI's default sorting."""

    @property
    def all_page_urls(self) -> List[str]:
        """The ``page_urls`` along with the ``homepage_url``."""
        return list(
            set([str(url) for url in self.page_urls] + [str(self.homepage_url)])
        )

    @validator("root_url")
    def validate_root_url(cls, v: str) -> str:
        """Validate the root url so it points to a directory, not a "file"."""
        parsed_url = urlparse(v)
        path = "/".join(
            [p for p in parsed_url.path.split("/") if not p.endswith(".html")]
        )
        if not path.endswith("/"):
            path = f"{path}/"
        new_url = (
            parsed_url[0],
            parsed_url[1],
            path,
            "",  # un-set params
            "",  # un-set query
            "",  # un-set fragment
        )
        return urlunparse(new_url)
