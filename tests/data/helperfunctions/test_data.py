"""
Pytests for data.py

Date:
    12-08-2023

"""
# pylint: skip-file

import pytest
import requests
from requests import Response

from data.helperfunctions import Data, get_data


URLS = [
    'https://api.energidataservice.dk/dataset/Elspotprices',
    'https://api.energidataservice.dk/dataset/DatahubPricelist'
]



"""==========================================   TEST   ===================================================="""

@pytest.mark.parametrize(
    ('input', 'expected'),
    (
        (Data(requests.get(URLS[0], timeout=5)), f"Data({URLS[0]})"),
        (Data(requests.get(URLS[1], timeout=5)), f"Data({URLS[1]})"),

    )
)
def test_data_class_repr(input, expected):
    assert input.__repr__() == expected


@pytest.mark.parametrize(
    ('input', 'expected', 'json_format'),
    (
        (requests.get(URLS[0], timeout=5), Data(requests.get(URLS[0], timeout=5)), True),
        (requests.get(URLS[1], timeout=5), Data(requests.get(URLS[1], timeout=5)), True),

    )
)
def test_data_class(input: Response, expected: Data, json_format: bool):
    assert input.status_code == expected.status_code
    assert input.content == expected.content
    
    if json_format:
        assert input.json() == expected.json


@pytest.mark.parametrize(
    ('input', 'json_format'),
    (
        (URLS[0], True),
        (URLS[1], True),
    )
)
def test_get_data(input: str, json_format: bool):
    data = Data(requests.get(input, timeout=5))
    expected = get_data(input)

    assert type(data) == type(expected)
    assert data.__repr__() == expected.__repr__()
    assert data.status_code == expected.status_code
    assert data.content == expected.content

    if json_format:
        assert data.json == expected.json
    

    
