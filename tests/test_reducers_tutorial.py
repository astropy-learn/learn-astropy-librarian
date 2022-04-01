# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Tests for the astropylibrarian.reducers.tutorial module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from astropylibrarian.reducers.tutorial import (
    ReducedNbcollectionTutorial,
    ReducedSphinxTutorial,
)

if TYPE_CHECKING:
    from .conftest import HtmlTestData


def test_color_excess(color_excess_tutorial: HtmlTestData) -> None:
    """Test with the "color-excess.html" dataset."""
    reduced_tutorial = ReducedSphinxTutorial(html_page=color_excess_tutorial)

    assert reduced_tutorial.url == color_excess_tutorial.url
    assert reduced_tutorial.h1 == (
        "Analyzing interstellar reddening and calculating synthetic photometry"
    )
    assert reduced_tutorial.authors == [
        "Kristen Larson",
        "Lia Corrales",
        "Stephanie T. Douglas",
        "Kelle Cruz",
    ]
    assert reduced_tutorial.keywords == [
        "dust extinction",
        "synphot",
        "astroquery",
        "units",
        "photometry",
        "extinction",
        "physics",
        "observational astronomy",
    ]
    assert reduced_tutorial.images[0] == (
        "http://learn.astropy.org/_images/color-excess_9_0.png"
    )
    assert reduced_tutorial.summary == (
        "In this tutorial, we will look at some extinction curves from the "
        "literature, use one of those curves to deredden an observed spectrum"
        ", and practice invoking a background source flux in order to "
        "calculate magnitudes from an extinction model."
    )

    assert reduced_tutorial.sections[0].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Learning Goals",
    ]
    assert reduced_tutorial.sections[1].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Companion Content",
    ]
    assert reduced_tutorial.sections[2].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry"
    ]
    assert reduced_tutorial.sections[2].content == reduced_tutorial.summary
    assert reduced_tutorial.sections[3].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Introduction",
    ]
    assert reduced_tutorial.sections[4].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Example 1: Investigate Extinction Models",
    ]
    assert reduced_tutorial.sections[5].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Example 2: Deredden a Spectrum",
    ]
    assert reduced_tutorial.sections[6].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Example 3: Calculate Color Excess with synphot",
        "Exercise",
    ]
    assert reduced_tutorial.sections[7].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Example 3: Calculate Color Excess with synphot",
    ]


def test_color_excess_v2(color_excess_tutorial_v2: HtmlTestData) -> None:
    """Test the reduction of the color_excess_v2 tutorial, which features
    a new section-based HTML structure.
    """
    reduced_tutorial = ReducedSphinxTutorial(
        html_page=color_excess_tutorial_v2
    )
    assert reduced_tutorial.url == color_excess_tutorial_v2.url
    assert reduced_tutorial.h1 == (
        "Analyzing interstellar reddening and calculating synthetic photometry"
    )
    assert reduced_tutorial.authors == [
        "Kristen Larson",
        "Lia Corrales",
        "Stephanie T. Douglas",
        "Kelle Cruz",
    ]
    assert reduced_tutorial.keywords == [
        "dust extinction",
        "synphot",
        "astroquery",
        "units",
        "photometry",
        "extinction",
        "physics",
        "observational astronomy",
    ]
    assert reduced_tutorial.images[0] == (
        "http://learn.astropy.org/_images/color-excess_9_0.png"
    )
    assert reduced_tutorial.summary == (
        "In this tutorial, we will look at some extinction curves from the "
        "literature, use one of those curves to deredden an observed spectrum"
        ", and practice invoking a background source flux in order to "
        "calculate magnitudes from an extinction model."
    )

    assert len(reduced_tutorial.sections) == 8

    assert reduced_tutorial.sections[0].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Learning Goals",
    ]
    assert reduced_tutorial.sections[1].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Companion Content",
    ]
    assert reduced_tutorial.sections[2].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry"
    ]
    assert reduced_tutorial.sections[2].content == reduced_tutorial.summary
    assert reduced_tutorial.sections[3].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Introduction",
    ]
    assert reduced_tutorial.sections[4].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Example 1: Investigate Extinction Models",
    ]
    assert reduced_tutorial.sections[5].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Example 2: Deredden a Spectrum",
    ]
    assert reduced_tutorial.sections[6].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Example 3: Calculate Color Excess with synphot",
        "Exercise",
    ]
    assert reduced_tutorial.sections[7].headings == [
        "Analyzing interstellar reddening and calculating synthetic "
        "photometry",
        "Example 3: Calculate Color Excess with synphot",
    ]


def test_coordinates_transform(
    coordinates_transform_tutorial: HtmlTestData,
) -> None:
    """Test with the "Coordinates_Transform.html" dataset."""
    reduced_tutorial = ReducedSphinxTutorial(
        html_page=coordinates_transform_tutorial
    )

    assert reduced_tutorial.url == coordinates_transform_tutorial.url
    assert reduced_tutorial.h1 == (
        "Coords 2: Transforming between coordinate systems"
    )
    assert reduced_tutorial.authors == [
        "Erik Tollerud",
        "Kelle Cruz",
        "Stephen Pardy",
        "Stephanie T. Douglas",
    ]
    assert reduced_tutorial.keywords == [
        "coordinates",
        "units",
        "observational astronomy",
    ]
    assert reduced_tutorial.images[0] == (
        "http://learn.astropy.org/_images/Coordinates-Transform_51_0.png"
    )
    assert reduced_tutorial.summary == (
        "In this tutorial we demonstrate how to define astronomical "
        "coordinates using the astropy.coordinates “frame” classes. We then "
        "show how to transform between the different built-in coordinate "
        "frames, such as from ICRS (RA, Dec) to Galactic (l, b). Finally, we "
        "show how to compute altitude and azimuth from a specific observing "
        "site."
    )
    for section in reduced_tutorial.sections:
        if section.header_level == 1:
            assert section.content == reduced_tutorial.summary


def test_nbcollection_coordinates_transform(
    nbcollection_coordinates_transform_tutorial: HtmlTestData,
) -> None:
    """Test with the nbcollection-generated "Coordinates_Transform.html"
    dataset.
    """
    test_data = nbcollection_coordinates_transform_tutorial  # shorten name

    reduced_tutorial = ReducedNbcollectionTutorial(html_page=test_data)

    assert reduced_tutorial.url == test_data.url
    assert reduced_tutorial.h1 == (
        "Astronomical Coordinates 2: "
        "Transforming Coordinate Systems and Representations"
    )
    assert reduced_tutorial.authors == ["Adrian Price-Whelan"]
    assert reduced_tutorial.keywords == [
        "coordinates",
        "OOP",
    ]
    assert len(reduced_tutorial.images) == 0  # all images are embedded here
    assert len(reduced_tutorial.sections) > 0


def test_nbcollection_coordinates_transform_2022_03(
    nbcollection_coordinates_transform_tutorial_2022_03: HtmlTestData,
) -> None:
    """Test with the nbcollection-generated
    ""
    dataset.
    """
    test_data = nbcollection_coordinates_transform_tutorial_2022_03

    reduced_tutorial = ReducedNbcollectionTutorial(html_page=test_data)

    assert reduced_tutorial.url == test_data.url
    assert reduced_tutorial.h1 == (
        "Astronomical Coordinates 2: "
        "Transforming Coordinate Systems and Representations"
    )
    assert reduced_tutorial.authors == ["Adrian Price-Whelan"]
    assert reduced_tutorial.keywords == [
        "coordinates",
        "OOP",
    ]
    assert len(reduced_tutorial.images) == 0  # all images are embedded here
    assert len(reduced_tutorial.sections) > 0
