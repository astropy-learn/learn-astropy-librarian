# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Basic APIs for dealing with resources on the web, such as web pages."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Type, TypeVar

import lxml.html

HtmlPageType = TypeVar("HtmlPageType", bound="HtmlPage")


@dataclass
class HtmlPage:
    """A representation of an HTML page and its context on the web."""

    html: str
    """The HTML content."""

    url: str
    """The URL that this page was downloaded from (which might be different
    from the ``request_url``).

    This URL is considered to be the "canonical URL."
    """

    request_url: Optional[str] = None
    """The URL that was originally requested to obtain this page, which might
    be different than the ``url`` if the server redirected.
    """

    headers: Mapping[str, Any] = field(default_factory=dict)
    """The HTTP response headers."""

    def parse(self) -> lxml.html.HtmlElement:
        """Parse the HTML content with ``lxml.html``."""
        return lxml.html.document_fromstring(self.html)

    @classmethod
    def from_path(cls: Type[HtmlPageType], *, path: Path, url: str) -> HtmlPageType:
        """Open an HtmlPage from a local file.

        Parameters
        ----------
        path : `pathlib.Path`
            Path to the local HTML file.
        url : `str`
            The URL where the tutorial is publised.
        """
        html = path.read_text()
        return cls(html=html, url=url)
