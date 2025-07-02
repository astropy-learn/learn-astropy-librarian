# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Tests for the astropylibrarian.algolia.records module."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from astropylibrarian.algolia.client import generate_index_epoch
from astropylibrarian.reducers.jupyterbook import JupyterBookPage
from astropylibrarian.reducers.tutorial import ReducedSphinxTutorial
from astropylibrarian.workflows.indexjupyterbook import (
    extract_homepage_metadata,
)

if TYPE_CHECKING:
    from .conftest import HtmlTestData


def test_tutorialsectionrecord(color_excess_tutorial: HtmlTestData) -> None:
    reduced_tutorial = ReducedSphinxTutorial(html_page=color_excess_tutorial)

    index_epoch = generate_index_epoch()
    records = [
        r
        for r in reduced_tutorial.iter_algolia_objects(
            index_epoch=index_epoch, priority=0
        )
    ]
    data = records[0]

    expected_object_ID = (
        "aHR0cDovL2xlYXJuLmFzdHJvcHkub3JnL3JzdC10dXRvcmlhbHMvY29sb3ItZXhjZXNz"
        "Lmh0bWwjbGVhcm5pbmctZ29hbHM=-QW5hbHl6aW5nIGludGVyc3RlbGxhciByZWRkZW5"
        "pbmcgYW5kIGNhbGN1bGF0aW5nIHN5bnRoZXRpYyBwaG90b21ldHJ5IExlYXJuaW5nIEd"
        "vYWxz"
    )

    # Get the indexedDatetime field out because it's dynamic
    indexed_datetime = data.pop("date_indexed")
    # Ensure it's formatted correctly
    datetime.datetime.strptime(indexed_datetime, "%Y-%m-%dT%H:%M:%S.%f")
    assert isinstance(
        datetime.datetime.fromisoformat(indexed_datetime), datetime.datetime
    )

    # Ensure that the structure of other sections matches the expectation
    assert data == {
        "objectID": expected_object_ID,
        "index_epoch": index_epoch,
        "root_url": color_excess_tutorial.url,
        "root_title": reduced_tutorial.h1,
        "root_summary": reduced_tutorial.summary,
        "base_url": color_excess_tutorial.url,
        "url": f"{color_excess_tutorial.url}#learning-goals",
        "content": (
            "Investigate extinction curve shapes "
            "Deredden spectral energy distributions and spectra "
            "Calculate photometric extinction and reddening "
            "Calculate synthetic photometry for a dust-reddened star by "
            "combining dust_extinction and synphot "
            "Convert from frequency to wavelength with astropy.unit "
            "equivalencies "
            "Unit support for plotting with astropy.visualization"
        ),
        "importance": 2,
        "authors": [
            "Kristen Larson",
            "Lia Corrales",
            "Stephanie T. Douglas",
            "Kelle Cruz",
        ],
        "content_type": "tutorial",
        "astropy_package_keywords": [
            "dust_extinction",
            "synphot",
            "astroquery",
            "units",
        ],
        "python_package_keywords": [],
        "task_keywords": [
            "photometry",
        ],
        "science_keywords": [
            "extinction",
            "physics",
            "observational astronomy",
        ],
        "h1": ("Analyzing interstellar reddening and calculating synthetic photometry"),
        "h2": "Learning Goals",
        "thumbnail_url": ("http://learn.astropy.org/_images/color-excess_48_1.png"),
        "priority": 0,
    }


def test_guiderecord(
    ccd_guide_00_00: HtmlTestData, ccd_guide_01_05: HtmlTestData
) -> None:
    metadata = extract_homepage_metadata(
        html_page=ccd_guide_00_00,
        root_url="http://www.astropy.org/ccd-reduction-and-photometry-guide/",
        priority=1,
    )
    page = JupyterBookPage(ccd_guide_01_05)
    index_epoch = generate_index_epoch()
    records = [
        r
        for r in page.iter_algolia_objects(
            site_metadata=metadata, index_epoch=index_epoch
        )
    ]
    data = records[0]

    assert data["objectID"] == (
        "aHR0cDovL3d3dy5hc3Ryb3B5Lm9yZy9jY2QtcmVkdWN0aW9uLWFuZC1waG90b21ldHJ5L"
        "Wd1aWRlL25vdGVib29rcy8wMS0wNS1jYWxpYnJhdGlvbi1vdmVydmlldy5odG1sI2Zpcn"
        "N0LXNvbWUtc3RhcnMtd2l0aC1ub2lzZQ==-MS40LiBDYWxpYnJhdGlvbiBvdmVydmlldy"
        "AxLjQuMS4gVGhpcyBub2lzZSBjYW5ub3QgYmUgcmVtb3ZlZCBmcm9tIENDRCBpbWFnZXM"
        "gMS40LjEuMS4gRmlyc3QsIHNvbWUgc3RhcnMgd2l0aCBub2lzZQ=="
    )
    assert data["index_epoch"] == index_epoch
    assert data["root_summary"] == (
        "The purpose of this text is to walk through image reduction and "
        "photometry using Python, especially Astropy and its affiliated "
        "packages. It assumes some basic familiarity with astronomical "
        "images and with Python. The inspiration for this work is a pair of "
        "guides written for IRAF, “A User’s Guide to CCD Reductions with "
        "IRAF” (Massey 1997) and “A User’s Guide to Stellar CCD Photometry "
        "with IRAF” (Massey and Davis 1992)."
    )
    assert data["content_type"] == "guide"
    assert data["url"] == (
        "http://www.astropy.org/ccd-reduction-and-photometry-guide/notebooks/"
        "01-05-Calibration-overview.html#first-some-stars-with-noise"
    )
    assert data["root_url"] == (
        "http://www.astropy.org/ccd-reduction-and-photometry-guide/"
    )
    assert data["root_title"] == "CCD Data Reduction Guide"
    assert data["base_url"] == (
        "http://www.astropy.org/ccd-reduction-and-photometry-guide/notebooks/"
        "01-05-Calibration-overview.html"
    )
    assert data["h1"] == "1.4. Calibration overview"
    assert data["h2"] == "1.4.1. This noise cannot be removed from CCD images"
    assert data["h3"] == "1.4.1.1. First, some stars with noise"
    assert data["importance"] == 4
    assert data["content"] == (
        "The image below shows stars (the larger “blobs” in the image) but "
        "shows quite a bit of noise as well (the much smaller “dots”)."
        "\n\nimage = np.zeros([2000, 2000]) gain = 1.0 noise_amount = 1500  "
        "stars_with_noise = imsim.stars(image, 50, max_counts=2000, fwhm=10) "
        "+ imsim.read_noise(image, noise_amount, gain=gain)  "
        "show_image(stars_with_noise, cmap='gray', percu=99.9) "
        "plt.title('Stars with noise')"
    )
    assert "date_indexed" in data
    date_indexed = datetime.datetime.fromisoformat(data["date_indexed"])
    assert isinstance(date_indexed, datetime.datetime)
    assert data["thumbnail_url"] == (
        "http://www.astropy.org/ccd-reduction-and-photometry-guide/_images/"
        "01-05-Calibration-overview_24_0.png" 
    )
    assert data["priority"] == 1
