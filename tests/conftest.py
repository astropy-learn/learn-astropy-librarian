"""Pytest configurations."""

from __future__ import annotations

from pathlib import Path

import pytest

from astropylibrarian.resources import HtmlPage


class HtmlTestData(HtmlPage):
    """A container for HTML pages cached in the repo's tests/data directory."""

    @classmethod
    def from_test_path(cls, *, path: str, url: str) -> HtmlTestData:
        data_path = Path(__file__).parent / "data"
        source_path = data_path.joinpath(Path(path))
        return cls.from_path(path=source_path, url=url)


@pytest.fixture(scope="session")
def color_excess_tutorial() -> HtmlTestData:
    """The color-excess.html tutorial page."""
    return HtmlTestData.from_test_path(
        path="tutorials/color-excess.html",
        url="http://learn.astropy.org/rst-tutorials/color-excess.html",
    )


@pytest.fixture(scope="session")
def color_excess_tutorial_v2() -> HtmlTestData:
    """The color-excess.html tutorial page obtained in 2021-06.

    This is the same content as `color_excess_tutorial`, but the HTML structure
    is now different (due to a change in Sphinx or Sphinx extensions?).
    Instead of div elements with "section" classes, sections now use the
    section tag itself without classes.
    """
    return HtmlTestData.from_test_path(
        path="tutorials/color-excess-v2.html",
        url="http://learn.astropy.org/rst-tutorials/color-excess.html",
    )


@pytest.fixture(scope="session")
def coordinates_transform_tutorial() -> HtmlTestData:
    """The Coordinates-Transform.html tutorial page."""
    return HtmlTestData.from_test_path(
        path="tutorials/Coordinates-Transform.html",
        url="http://learn.astropy.org/rst-tutorials/"
        "Coordinates-Transform.html",
    )


@pytest.fixture(scope="session")
def nbcollection_coordinates_transform_tutorial() -> HtmlTestData:
    """The nbcollection-generated Coordinates-Transform.html tutorial page."""
    return HtmlTestData.from_test_path(
        path="nbcollection-tutorials/2-Coordinates-Transforms.html",
        url="http://learn.astropy.org/tutorials/2-Coordinates-Transforms.html",
    )


@pytest.fixture(scope="session")
def nbcollection_coordinates_transform_tutorial_2022_03() -> HtmlTestData:
    """The nbcollection-generated Coordinates-Transform.html tutorial page,
    newly reformatted as of 2022-03.
    """
    return HtmlTestData.from_test_path(
        path="nbcollection-tutorials/2-Coordinates-Transforms-2022-03.html",
        url="http://learn.astropy.org/tutorials/2-Coordinates-Transforms.html",
    )


@pytest.fixture(scope="session")
def ccd_guide_index() -> HtmlTestData:
    """The ``ccd-guide/index.html`` page.

    This page is the root file created by Jupyter Book, but which redirects
    to the first content page (notebooks/00-00-Preface.html).
    """
    return HtmlTestData.from_test_path(
        path="ccd-guide/index.html",
        url="http://www.astropy.org/ccd-reduction-and-photometry-guide/"
        "index.html",
    )


@pytest.fixture(scope="session")
def ccd_guide_00_00() -> HtmlTestData:
    """The ``ccd-guide/notebooks/00-00-Preface.html`` page.

    This is the CCD Guide homepage created by Jupyter Book.
    """
    return HtmlTestData.from_test_path(
        path="ccd-guide/notebooks/00-00-Preface.html",
        url="http://www.astropy.org/ccd-reduction-and-photometry-guide/"
        "notebooks/00-00-Preface.html",
    )


@pytest.fixture(scope="session")
def ccd_guide_01_05() -> HtmlTestData:
    """The ``ccd-guide/notebooks/01-05-Calibration-overview.html`` page.

    This is a regular content page from the CCD Guide homepage created by
    Jupyter Book.
    """
    return HtmlTestData.from_test_path(
        path="ccd-guide/notebooks/01-05-Calibration-overview.html",
        url="http://www.astropy.org/ccd-reduction-and-photometry-guide/"
        "notebooks/01-05-Calibration-overview.html",
    )
