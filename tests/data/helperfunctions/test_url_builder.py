"""
Pytests for url_builder.py

Date:
    25-09-2023

"""
#pylint: skip-file

import pytest
from datetime import datetime, date, timedelta

from data.helperfunctions import URLBuilder
from data.electricity.tariff_company import TARIFF_COMPANY

TEST_URL = {
        'base': 'https://www.dr.dk',
        'params': {
            'sporten': '',
            'resultater': '',
            'fodbold': '',
        },
        'delimiters': [('/'), ('', '/'), ('', '/'), ('', '')]
    }

URLS = [
    # SpotPrice URL
    {
        'base': 'https://api.energidataservice.dk/dataset/Elspotprices',
        'params': {
            'offset': '0',
            'start': '',
            'columns': '"HourDK","PriceArea","SpotPriceDKK"',
            'filter': '',
            'sort': 'HourDK%20ASC'
        },
        'delimiters': [('?'), ('=', '&'), ('=', '&'), ('=', '&'), ('=', '&'), ('=', '')]
    },

    # Tariff URL
    {
        'base': 'https://api.energidataservice.dk/dataset/DatahubPricelist',
        'params': {
            'offset': '0',
            'end': '',
            'columns': '''"ChargeTypeCode","ValidFrom","ValidTo", \
                       "Price1","Price2","Price3","Price4","Price5",
                       "Price6","Price7","Price8","Price9","Price10",
                       "Price11","Price12","Price13","Price14","Price15",
                       "Price16","Price17","Price18","Price19","Price20",
                       "Price21","Price22","Price23","Price24"'''.replace(' ', ''),
            'filter': '',
            'sort': 'ValidFrom%20DESC&timezone=dk'
        },
        'delimiters': [('?'), ('=', '&'), ('=', '&'), ('=', '&'), ('=', '&'), ('=', '')]
    },
]

@pytest.fixture
def time_window():
    todays_date = date.today()
    return (datetime(todays_date.year, todays_date.month, todays_date.day, 0, 0, 0), 
            (datetime(todays_date.year, todays_date.month, todays_date.day, 23, 00, 00) + timedelta(1)))

"""=========================================   TESTS   ==================================================="""

def test_url_builder_init():
    expected_url = "https://www.dr.dk/sporten/resultater/fodbold"
    url = URLBuilder(TEST_URL).url

    assert url == expected_url


def test_url_builder_repr():
    expected_str = f"URLBuilder(url=https://www.dr.dk/sporten/resultater/fodbold)"
    
    assert URLBuilder(TEST_URL).__repr__() == expected_str
    

@pytest.mark.parametrize(
    ('input'),
    (
        ("DK1"),
        ("DK2"),
    )
)
def test_build_spot_price_url(input):
    todays_date = date.today()

    base = 'https://api.energidataservice.dk/dataset/Elspotprices'
    offset = 'offset=0'
    start = f'start={todays_date}'
    columns = 'columns="HourDK","PriceArea","SpotPriceDKK"'
    filter1 = f'"PriceArea":["{input}"]'
    filtering = 'filter={' + filter1 + '}'
    sorting = 'sort=HourDK%20ASC'
    expected_url = f"{base}?{offset}&{start}&{columns}&{filtering}&{sorting}"

    URLS[0]["params"]["start"] = f'{todays_date}'
    URLS[0]["params"]["filter"] = '{' + filter1 + '}'
    url = URLBuilder(URLS[0]).url

    assert url == expected_url


@pytest.mark.parametrize(
    ('input'),
    (
        ("Ikast El Net A/S"),
    )
)
def test_build_tariff_url(input, time_window):
    gln = TARIFF_COMPANY[input]["gln"]
    charge_type_codes = TARIFF_COMPANY[input]["type"]
    codes = f'{list(charge_type_codes)}'
    codes = codes.replace("'", '"')
    
    base = 'https://api.energidataservice.dk/dataset/DatahubPricelist'
    offset = 'offset=0'
    end = f'end={time_window[1].date()}'
    prices = \
    '''"Price1","Price2","Price3","Price4","Price5",
    "Price6","Price7","Price8","Price9","Price10",
    "Price11","Price12","Price13","Price14","Price15",
    "Price16","Price17","Price18","Price19","Price20",
    "Price21","Price22","Price23","Price24"'''
    prices = prices.replace(" ", "")
    columns = f'columns="ChargeTypeCode","ValidFrom","ValidTo",{prices}'
    filter1 = f'"GLN_Number":["{gln}"]'
    filter2 = f'"ChargeTypeCode":{codes}'
    filtering = "filter={" + filter1 + ',' + filter2 + '}'
    sorting = 'sort=ValidFrom%20DESC&timezone=dk'
    expected_url = f"{base}?{offset}&{end}&{columns}&{filtering}&{sorting}"

    URLS[1]["params"]["end"] = f"{time_window[1].date()}"
    URLS[1]["params"]["filter"] = '{' + filter1 + ',' + filter2 + '}'
    url = URLBuilder(URLS[1]).url

    assert url == expected_url


def test_set_params():
    random_url = {
        "params": {
            "LOWER": 0,
            "CASE": "test",
            "not change": [],
            "": False,
            "PLEASE": (),
            "dont change": 41,
        }
    }

    expected_url = {
        "params": {
            "lower": 0,
            "case": "test",
            "not change": [],
            "": False,
            "please": (),
            "dont change": 41,
        }
    }

    url = URLBuilder.set_params(random_url, params=[("LOWER", "lower"),
                                                    ("CASE", "case"),
                                                    ("PLEASE", "please")])

    assert random_url != expected_url
    assert url == expected_url


def test_set_values():
    random_url = {
        "params": {
            "number": "27",
            "text": "",
            "some": "test",
            "name": "John",
            "empty": ""
        }
    }

    expected_url = {
        "params": {
            "number": "27",
            "text": "some text",
            "some": "test",
            "name": "John",
            "empty": "not empty"
        }
    }

    url = URLBuilder.set_values(random_url, values=["some text", "not empty"])

    assert random_url != expected_url
    assert url == expected_url