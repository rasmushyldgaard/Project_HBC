"""
Pytests for parser.py

Date:
    18-09-2023

"""
#pylint: skip-file

import pytest
from datetime import datetime, date

from data.helperfunctions import Parser


"""=========================================   TESTS   ==================================================="""

def test_parse_spot_price():
    price = 779.520020
    expected_price = 0.7795

    assert Parser.parse_spot_price(price) == expected_price


def test_parse_time():
    time = "2023-08-20T18:00:00"
    expected_time = datetime(2023, 8, 20, 18, 00, 00)

    assert Parser.parse_time(time) == expected_time


def test_parse_iso_time():
    time = "2023-09-14T17:00:00.0000000Z"
    expected_time = datetime(2023, 9, 14, 17, 00, 00)

    assert Parser.parse_iso_time(time) == expected_time

def test_parse_date():
    date_1 = "2023-10-04"
    expected_date = date(2023, 10, 4)

    assert Parser.parse_date(date_1) == expected_date



