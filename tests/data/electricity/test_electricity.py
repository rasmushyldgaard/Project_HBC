"""
Pytests for electricity.py

Date:
    10-09-2023

"""
#pylint: skip-file

import pytest
from datetime import datetime

from data.electricity import Electricity
from data.electricity.spot_price import SpotPrice
from data.electricity.tariff import Tariff
from data.electricity.provider import Provider
from data.electricity.flat_charges import FlatCharges

@pytest.fixture
def spot_price():
    return SpotPrice(datetime(2023, 8, 19, 13, 00, 00), "DK1", 1.14)

@pytest.fixture
def tariff():
    return Tariff(datetime(2022, 12, 24, 23, 00, 00), 0.69)

@pytest.fixture
def provider():
    return Provider(datetime(2023, 9, 24, 16, 00, 00), 0.5)

@pytest.fixture
def flat_charges():
    return FlatCharges()

@pytest.fixture
def electricity(spot_price: SpotPrice, tariff: Tariff, provider: Provider):
    return Electricity(spot_price, tariff, provider)

"""=========================================   TESTS   ==================================================="""

def test_electricity_class(electricity: Electricity, spot_price: SpotPrice, 
                           tariff: Tariff, provider: Provider, flat_charges: FlatCharges):
    expected_time = tariff.time
    expected_price = round((spot_price.price + tariff.price + provider.price + flat_charges.total)*1.25, 4)

    assert electricity.time == expected_time
    assert electricity.price == expected_price
    assert electricity.spot_price == spot_price
    assert electricity.tariff == tariff
    assert electricity.provider == provider
    assert electricity.flat_charges == flat_charges


def test_electricity_repr(electricity: Electricity):
    expected_str = f"Electricity(time=2022-12-24 23:00:00, price=3.9238)"

    assert electricity.__repr__() == expected_str


def test_electricity_comparison(electricity: Electricity):
    electricity_1 = Electricity(SpotPrice(datetime(2023, 8, 19, 23, 00, 00), "DK1", 0.98),
                                Tariff(datetime(2022, 1, 7, 8, 00, 00), 0.5),
                                Provider(datetime(2024, 10, 12, 00, 00, 00), 0))
    electricity_2 = Electricity(SpotPrice(datetime(2022, 1, 7, 8, 00, 00), "DK2", 1.20),
                                Tariff(datetime(2024, 8, 19, 23, 00, 00), 1),
                                Provider(datetime(2023, 12, 12, 23, 00, 00), 0.85))
    electricity_3 = Electricity(SpotPrice(datetime(2023, 8, 19, 13, 00, 00), "DK1", 1.14),
                                Tariff(datetime(2022, 12, 24, 23, 00, 00), 0.69),
                                Provider(datetime(2023, 1, 31, 8, 00, 00), 0.5))

    assert electricity_1 < electricity
    assert electricity_2 > electricity
    assert electricity_3 == electricity