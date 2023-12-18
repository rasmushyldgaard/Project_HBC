"""
Pytests for spot_price.py

Date:
    19-08-2023

"""
# pylint: skip-file

import pytest
from datetime import datetime

from data.electricity.spot_price import SpotPrice


@pytest.fixture
def spot_price():
    spot_price = SpotPrice(datetime(2023, 8, 19, 13, 00, 00), "DK1", 1.14)
    return spot_price

"""=========================================   TESTS   ==================================================="""

def test_spot_price_class(spot_price: SpotPrice):
    expected_time = datetime(2023, 8, 19, 13, 00, 00)
    expected_price_area = "DK1"
    expected_price = 1.14

    assert spot_price.time == expected_time
    assert spot_price.price_area == expected_price_area
    assert spot_price.price == expected_price


def test_spot_price_repr(spot_price: SpotPrice):
    expected_str = f"SpotPrice(time=2023-08-19 13:00:00, price_area=DK1, price=1.14)"

    assert spot_price.__repr__() == expected_str


def test_spot_price_comparison(spot_price: SpotPrice):
    spot_price_1 = SpotPrice(datetime(2023, 8, 19, 23, 00, 00), "DK1", 0.98)
    spot_price_2 = SpotPrice(datetime(2022, 1, 7, 8, 00, 00), "DK2", 1.20)
    spot_price_3 = SpotPrice(datetime(2023, 12, 12, 13, 00, 00), "DK2", 1.14)

    assert spot_price_1 < spot_price
    assert spot_price_2 > spot_price
    assert spot_price_3 == spot_price
