# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Reduce the HTML source of a learn.astropy tutorial page (notebook-based)
into search records.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Type
from urllib.parse import urljoin

from astropylibrarian.algolia.records import TutorialRecord
from astropylibrarian.keywords import KeywordDb
from astropylibrarian.reducers.utils import (
    Section,
    iter_nbcollection_sections,
    iter_sphinx_sections,
)

if TYPE_CHECKING:
    import lxml.html

    from astropylibrarian.resources import HtmlPage

__all__ = [
    "ReducedTutorial",
    "ReducedSphinxTutorial",
    "ReducedNbcollectionTutorial",
]

logger = getLogger(__name__)


def get_tutorial_reducer(html_page: HtmlPage) -> Type[ReducedTutorial]:
    """Get the reducer appropriate for the tutorial's structure."""
    doc = html_page.parse()
    if len(doc.cssselect(".jp-Notebook")) > 0:
        logger.debug("Using nbcollection tutorial reducer")
        return ReducedNbcollectionTutorial
    else:
        logger.debug("Using sphinx tutorial reducer")
        return ReducedSphinxTutorial


class ReducedTutorial:
    """A reduction of a notebook-based learn.astropy tutorial page into search
    records.

    Parameters
    ----------
    html_page : `astropylibrarian.resources.HtmlPage`
        The downloaded HTML page.
    """

    @property
    def url(self) -> str:
        """The canonical URL of the tutorial page."""
        return self._url

    @property
    def h1(self) -> str:
        """The tutorial's H1 headline text."""
        return self._h1

    @property
    def authors(self) -> List[str]:
        """The names of authors declared by the tutorial page."""
        return self._authors

    @property
    def keywords(self) -> List[str]:
        """The keywords declared by the tutorial page."""
        return self._keywords

    @property
    def summary(self) -> str:
        """The tutorial's summary paragraph."""
        return self._summary

    @property
    def images(self) -> List[str]:
        """The URLs of images in the tutorial content."""
        return self._images

    @property
    def sections(self) -> List[Section]:
        """The sections (`astropylibrarian.reducers.utils.Section`) that
        are found within the content.
        """
        return self._sections

    def __init__(self, *, html_page: HtmlPage) -> None:
        self._url = html_page.url
        self._h1: str = ""
        self._authors: List[str] = []
        self._keywords: List[str] = []
        self._summary = ""
        self._images: List[str] = []
        self._sections: List["Section"] = []

        # These are headings for sections that should be ignored because
        # they're part of the metadata.
        self.ignored_headings = set(["authors", "keywords", "summary"])

        self.process_html(html_page)

        self._set_summary_on_h1_section()

    def process_html(self, html_page: HtmlPage) -> None:
        """Process the HTML page."""
        raise NotImplementedError

    def _is_ignored_section(self, section: Section) -> bool:
        """Determine if a section should be ignored.

        Uses the `ignored_headings` attribute to determine if a section should
        be ignored.

        Returns
        -------
        bool
            `True` if the section should be ignored; `False` if it should be
            accepted.
        """
        section_headings = set([h.lower() for h in section.headings])
        if section_headings.intersection(self.ignored_headings):
            return True
        else:
            return False

    def iter_records(
        self, *, index_epoch: str, priority: int
    ) -> Iterator[TutorialRecord]:
        """Iterate over Algolia records in the tutorial."""
        keyworddb = KeywordDb.load()
        for section in self.sections:
            yield TutorialRecord.from_section(
                tutorial=self,
                section=section,
                keyworddb=keyworddb,
                index_epoch=index_epoch,
                priority=priority,
            )

    def iter_algolia_objects(
        self, *, index_epoch: str, priority: int
    ) -> Iterator[Dict[str, Any]]:
        """Iterate over all objects that are extractable from the tutorial in
        a format ready to use with the algoliasearch client.

        Yields
        ------
        dict
            An object compatible with algolia search ``save_objects``-type
            methods.
        """
        for record in self.iter_records(
            index_epoch=index_epoch, priority=priority
        ):
            yield from record.export_capped_records_to_algolia()

    def _set_summary_on_h1_section(self) -> None:
        """Replaces the content of the "h1" section, which should be empty,
        with the summary.
        """
        for section in self.sections:
            if section.header_level == 1:
                section.content = self.summary

    @staticmethod
    def _parse_comma_list(element: lxml.html.HtmlElement) -> List[str]:
        content = element.text_content()
        return [s.strip() for s in content.split(",")]


class ReducedSphinxTutorial(ReducedTutorial):
    """A reduced tutorial notebook that was published in a Sphinx site."""

    def process_html(self, html_page: HtmlPage) -> None:
        """Process the HTML page."""
        doc = html_page.parse()

        try:
            self._h1 = self._get_section_title(doc.cssselect("h1")[0])
        except IndexError:
            pass

        try:
            authors_paragraph = doc.cssselect(
                ".card section p, .card .section p"
            )[0]
            self._authors = self._parse_comma_list(authors_paragraph)
        except IndexError:
            pass

        try:
            keywords_paragraph = doc.cssselect("#keywords p")[0]
            self._keywords = self._parse_comma_list(keywords_paragraph)
        except IndexError:
            pass

        try:
            summary_paragraph = doc.cssselect("#summary p")[0]
            self._summary = summary_paragraph.text_content().replace("\n", " ")
        except IndexError:
            pass

        image_elements = doc.cssselect(".card section img, .card .section img")
        for image_element in image_elements:
            img_src = image_element.attrib["src"]
            self._images.append(urljoin(self.url, img_src))

        root_section = doc.cssselect(".card .section, .card section")[0]
        for s in iter_sphinx_sections(
            base_url=self._url,
            root_section=root_section,
            headers=[],
            header_callback=lambda x: x.rstrip("¶"),
            content_callback=clean_content,
        ):
            if not self._is_ignored_section(s):
                self._sections.append(s)

        # Also look for additional h1 section on the page.
        # Technically, the page should only have one h1, and all content
        # should be subsections of that. In real life, though, it's easy
        # to accidentally use additional h1 eleemnts for subsections.
        h1_heading = self._sections[-1].headings[-1]
        for sibling in root_section.itersiblings(tag=("div", "section")):
            if sibling.tag == "div" and "section" not in sibling.classes:
                continue
            for s in iter_sphinx_sections(
                root_section=sibling,
                base_url=self._url,
                headers=[h1_heading],
                header_callback=lambda x: x.rstrip("¶"),
                content_callback=clean_content,
            ):
                if not self._is_ignored_section(s):
                    self._sections.append(s)

    @staticmethod
    def _get_section_title(element: lxml.html.HtmlElement) -> str:
        return element.text_content().rstrip("¶")


class ReducedNbcollectionTutorial(ReducedTutorial):
    """A reduced tutorial notebook that was published with
    nbcollection/nbconvert.
    """

    def process_html(self, html_page: HtmlPage) -> None:
        """Process the HTML page."""
        doc = html_page.parse()

        try:
            self._h1 = (
                doc.cssselect("h1")[0].text_content().rstrip("¶").strip()
            )
        except IndexError:
            logger.warning("Did not find h1")
            pass

        try:
            authors_paragraph = doc.cssselect("#Authors + p")[0]
            self._authors = self._parse_comma_list(authors_paragraph)
        except IndexError:
            logger.warning("Did not find authors")
            pass

        try:
            keywords_paragraph = doc.cssselect("#Keywords + p")[0]
            self._keywords = self._parse_comma_list(keywords_paragraph)
        except IndexError:
            logger.warning("Did not find keywords")
            pass

        try:
            summary_paragraph = doc.cssselect("#Summary + p")[0]
            self._summary = summary_paragraph.text_content().replace("\n", " ")
        except IndexError:
            logger.warning("Did not find summary")
            pass

        image_elements = doc.cssselect("img")
        for image_element in image_elements:
            img_src = image_element.attrib["src"]
            if img_src.startswith("data:"):
                # skip embedded images
                continue
            self._images.append(urljoin(self.url, img_src))

        self._sections = []
        root_element = doc.cssselect(".jp-Notebook")[0]
        logger.debug("Got root element %s", root_element)
        for s in iter_nbcollection_sections(
            root_element=root_element,
            base_url=html_page.url,
            header_callback=lambda x: x.rstrip("¶"),
            content_callback=clean_content,
        ):
            if not self._is_ignored_section(s):
                self._sections.append(s)
            else:
                logger.debug("Ignored section")
        logger.debug("Found %s section in total", len(self._sections))


def clean_content(x: str) -> str:
    x = x.strip()
    x = x.replace(r"\n", " ")
    x = x.replace("\n", " ")
    x = x.replace("\\", " ")
    return x
