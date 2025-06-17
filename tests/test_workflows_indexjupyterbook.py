# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Tests for the astropylibrarian.workflows.indexjupyterbook module."""

from __future__ import annotations

from typing import Union

import pytest

from astropylibrarian.workflows.indexjupyterbook import (
    detect_redirect,
    extract_homepage_metadata,
)

from .conftest import HtmlTestData


@pytest.mark.parametrize(
    "html_path,base_url,expected",
    [
        (
            "ccd-guide/index.html",
            "https://www.astropy.org/ccd-reduction-and-photometry-guide/",
            "https://www.astropy.org/ccd-reduction-and-photometry-guide/"
            "notebooks/00-00-Preface.html",
        ),
        (
            "ccd-guide/index.html",
            "https://www.astropy.org/ccd-reduction-and-photometry-guide/index.html",
            "https://www.astropy.org/ccd-reduction-and-photometry-guide/"
            "notebooks/00-00-Preface.html",
        ),
        (
            "ccd-guide/notebooks/00-00-Preface.html",
            "https://www.astropy.org/ccd-reduction-and-photometry-guide/index.html",
            None,
        ),
    ],
)
def test_detect_redirect(
    html_path: str, base_url: str, expected: Union[None, str]
) -> None:
    html_page = HtmlTestData.from_test_path(path=html_path, url=base_url)
    assert expected == detect_redirect(html_page)


def test_extract_homepage_metadata(ccd_guide_00_00: HtmlTestData) -> None:
    """Test the extract_homepage_metadata function."""
    md = extract_homepage_metadata(
        html_page=ccd_guide_00_00,
        root_url="http://www.astropy.org/ccd-reduction-and-photometry-guide/",
        priority=1,
    )
    assert md.title == "CCD Data Reduction Guide"
    assert md.logo_url == (
        "http://www.astropy.org/ccd-reduction-and-photometry-guide/_static/logo.png"
    )
    assert md.description == (
        "The purpose of this text is to walk through image reduction and "
        "photometry using Python, especially Astropy and its affiliated "
        "packages. It assumes some basic familiarity with astronomical images "
        "and with Python. The inspiration for this work is a pair of guides "
        "written for IRAF, “A User’s Guide to CCD Reductions with IRAF” "
        "(Massey 1997) and “A User’s Guide to Stellar CCD Photometry with "
        "IRAF” (Massey and Davis 1992)."
    )
    assert md.source_repository == (
        "https://github.com/mwcraig/ccd-reduction-and-photometry-guide"
    )
    assert (
        "http://www.astropy.org/ccd-reduction-and-photometry-guide/notebooks/"
        "01-00-Understanding-an-astronomical-CCD-image.html"
    ) in md.page_urls
    assert md.priority == 1
