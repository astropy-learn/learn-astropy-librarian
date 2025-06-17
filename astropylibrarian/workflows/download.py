# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Workflow for downloading an HTML page."""

__all__ = ["download_html"]

from typing import TYPE_CHECKING

from astropylibrarian.resources import HtmlPage

if TYPE_CHECKING:
    import aiohttp


async def download_html(*, url: str, http_client: "aiohttp.ClientSession") -> HtmlPage:
    """Asynchronously download an HTML page (awaitable function).

    Parameters
    ----------
    url : `str`
        A URL for an HTML page.
    http_client : `aiohttp.ClientSession`
        An open aiohttp client.

    Returns
    -------
    html_page : `astropylibrarian.resources.HtmlPage`
        The downloaded HTML page.

    Raises
    ------
    DownloadError
        Raised if there is an error downloading a resource.
    """
    async with http_client.get(url) as resp:
        if resp.status != 200:
            raise DownloadError(f"url={url}")
        content = await resp.text()
        return HtmlPage(
            html=content,
            request_url=url,
            url=str(resp.url),
            headers=resp.headers,
        )


class DownloadError(RuntimeError):
    """Raised if there is an error downloading a resource."""
