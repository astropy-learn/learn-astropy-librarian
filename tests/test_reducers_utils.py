# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Tests for the astropylibrarian.reducers.utils module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from astropylibrarian.reducers.utils import iter_sphinx_sections

if TYPE_CHECKING:
    from .conftest import HtmlTestData


def test_iter_sphinx_sections(color_excess_tutorial: HtmlTestData) -> None:
    """Test the iter_sphinx_sections algorithm using the color-excess.html
    notebook tutorial example.

    This example is made complicated by the fact that the heading levels are
    not strictly hierarchical. There are multiple "h1" tags.
    """
    doc = color_excess_tutorial.parse()
    root = doc.cssselect(".card .section")[0]

    sections = []
    for s in iter_sphinx_sections(
        root_section=root,
        base_url=color_excess_tutorial.url,
        headers=[],
        header_callback=lambda x: x.rstrip("¶"),
        content_callback=lambda x: x.strip(),
    ):
        sections.append(s)

    assert len(sections) == 5

    assert sections[0].headings == [
        "Analyzing interstellar reddening and calculating synthetic photometry",
        "Learning Goals",
    ]
    assert sections[0].header_level == 2
    assert sections[0].url == (
        "http://learn.astropy.org/rst-tutorials/color-excess.html#learning-goals"
    )
    assert sections[0].content.startswith("Investigate extinction curve shapes")

    assert sections[1].headings[-1] == "Keywords"
    assert sections[1].header_level == 2
    assert sections[1].content.startswith(
        "dust extinction, synphot, astroquery, units, photometry, extinction,"
    )

    assert sections[2].headings[-1] == "Companion Content"
    assert sections[2].header_level == 2
    assert sections[2].content.startswith("Bessell & Murphy")

    assert sections[3].headings[-1] == "Summary"
    assert sections[3].header_level == 2
    assert sections[3].content.startswith(
        "In this tutorial, we will look at some extinction curves from the"
    )

    assert sections[4].headings[-1] == (
        "Analyzing interstellar reddening and calculating synthetic photometry"
    )
    assert sections[4].header_level == 1

    # Demonstrate finding addition h1 sections on a page (that are supposed
    # to be additional h2 sections in a hierarchical sense).
    h1_heading = sections[-1].headings[-1]
    for sibling in root.itersiblings(tag="div"):
        if "section" in sibling.classes:
            for s in iter_sphinx_sections(
                root_section=sibling,
                base_url=color_excess_tutorial.url,
                headers=[h1_heading],
                header_callback=lambda x: x.rstrip("¶"),
                content_callback=lambda x: x.strip(),
            ):
                sections.append(s)

    assert sections[5].header_level == 2
    assert sections[5].headings == [
        "Analyzing interstellar reddening and calculating synthetic photometry",
        "Introduction",
    ]

    assert sections[6].header_level == 2
    assert sections[6].headings == [
        "Analyzing interstellar reddening and calculating synthetic photometry",
        "Example 1: Investigate Extinction Models",
    ]

    assert sections[7].header_level == 2
    assert sections[7].headings == [
        "Analyzing interstellar reddening and calculating synthetic photometry",
        "Example 2: Deredden a Spectrum",
    ]

    assert sections[8].header_level == 3
    assert sections[8].headings == [
        "Analyzing interstellar reddening and calculating synthetic photometry",
        "Example 3: Calculate Color Excess with synphot",
        "Exercise",
    ]

    assert sections[9].header_level == 2
    assert sections[9].headings == [
        "Analyzing interstellar reddening and calculating synthetic photometry",
        "Example 3: Calculate Color Excess with synphot",
    ]
