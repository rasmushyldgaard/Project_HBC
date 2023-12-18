"""
Module for requesting raw data from the Internet

Date:
    12-08-2023

"""

import requests

from requests import Response
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Data:
    """ Class for storing 'raw' data content """
    _response: Response

    def __repr__(self) -> str:
        return f"Data({self._response.url})"

    @property
    def status_code(self) -> int:
        """ Get HTTP response status code """
        return self._response.status_code

    @property
    def content(self) -> bytes:
        """ Get HTTP response content """
        return self._response.content

    @property
    def json(self) -> Any:
        """ Get JSON format of content (only if the data was originally in JSON format!) """
        return self._response.json()


def get_data(url: str) -> Data:
    """
    Request data at specified URL and return Data object
    
    Args:
        url: API link to data as str

    Returns:
        A Data object for storing the URL content

    """
    return Data(requests.get(url, timeout=5))













