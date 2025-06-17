# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Tests for the astropylibrarian.reducers.jupyterbook module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urljoin

from astropylibrarian.reducers.jupyterbook import JupyterBookPage

if TYPE_CHECKING:
    from tests.conftest import HtmlTestData


def test_jupyterbookpage_sections(ccd_guide_01_05: HtmlTestData) -> None:
    page = JupyterBookPage(ccd_guide_01_05)
    sections = [s for s in page.iter_sections()]
    assert len(sections) > 0


def test_page_urls(ccd_guide_00_00: HtmlTestData) -> None:
    page = JupyterBookPage(ccd_guide_00_00)
    page_urls = set(page.page_urls)

    expected_paths = [
        "01-00-Understanding-an-astronomical-CCD-image.html",
        "01-01-astronomical-CCD-image-components.html",
        "01-03-Construction-of-an-artificial-but-realistic-image.html",
        "01-04-Nonuniform-sensitivity.html",
        "01-05-Calibration-overview.html",
        "01-06-Image-combination.html",
        "01-08-Overscan.html",
        "01-09-Calibration-choices-you-need-to-make.html",
        "01-11-reading-images.html",
        "02-00-Handling-overscan-trimming-and-bias-subtraction.html",
        "02-01-overscan-trimming-and-bias-subtraction-background.html",
        "02-02-Calibrating-bias-images.html",
        "02-04-Combine-bias-images-to-make-master.html",
        "03-00-Dark-current-and-hot-pixels.html",
        "03-01-Dark-current-The-ideal-case.html",
        "03-02-Real-dark-current-noise-and-other-artifacts.html",
        "03-04-Handling-overscan-and-bias-for-dark-frames.html",
        "03-05-Calibrate-dark-images.html",
        "03-06-Combine-darks-for-use-in-later-calibration-steps.html",
        "05-00-Flat-corrections.html",
        "05-01-about-flat-corrections.html",
        "05-03-Calibrating-the-flats.html",
        "05-04-Combining-flats.html",
        "06-00-Reducing-science-images.html",
        "06-03-science-images-calibration-examples.html",
        "08-00-Image-masking.html",
        "08-01-Identifying-hot-pixels.html",
        "08-02-Creating-a-mask.html",
        "08-03-Cosmic-ray-removal.html",
        "08-05-incorporating-masks-into-calibrated-science-images.html",
    ]
    expected_urls = set([urljoin(page.html_page.url, p) for p in expected_paths])
    assert expected_urls == page_urls
