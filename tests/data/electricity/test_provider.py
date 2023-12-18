"""
Pytests for provider.py

Date:
    24-09-2023

"""
#pylint: skip-file

import pytest

from datetime import datetime, date, timedelta, time

from data.electricity.provider import Provider, _create_hourly_provider


PRICES = {
    "HourlyPrice": {
        time(5, 0, 0): 0,
        time(9, 0, 0): 0.36,
        time(13, 0, 0): 0.2,
        time(22, 0, 0): 0.36,
        time(23, 59, 59): 0.2
    },
    "FlatPrice": {
        time(23, 59, 59): 0.5
    }
}

@pytest.fixture
def provider():
    return Provider(datetime(2023, 9, 24, 15, 00, 00), 0.69)

@pytest.fixture
def time_window():
    todays_date = date.today()
    return (datetime(todays_date.year, todays_date.month, todays_date.day, 0, 0, 0), 
            (datetime(todays_date.year, todays_date.month, todays_date.day, 23, 00, 00) + timedelta(1)))

def expected_time(index: int) -> datetime:        
    return (date.today() + timedelta(1)) + timedelta(hours=index)

"""=========================================   TESTS   ==================================================="""

def test_provider_class(provider: Provider):
    expected_time = datetime(2023, 9, 24, 15, 00, 00)
    expected_price = 0.69

    assert provider.time == expected_time
    assert provider.price == expected_price


def test_provider_repr(provider: Provider):
    expected_str = "Provider(time=2023-09-24 15:00:00, price=0.69)"

    assert provider.__repr__() == expected_str


def test_provider_comparison(provider: Provider):
    provider_1 = Provider(datetime(2024, 8, 19, 23, 00, 00), 0)
    provider_2 = Provider(datetime(2023, 9, 24, 15, 00, 00), 1.20)
    provider_3 = Provider(datetime(2022, 12, 12, 13, 00, 00), 0.69)

    assert provider > provider_1
    assert provider < provider_2
    assert provider == provider_3

@pytest.mark.parametrize(
    ('input', 'expected', 'index'),
    (
        (PRICES['HourlyPrice'], Provider(expected_time(0), 0), 24),
        (PRICES['HourlyPrice'], Provider(expected_time(1), 0), 1),
        (PRICES['HourlyPrice'], Provider(expected_time(5), 0.36), 5),
        (PRICES['HourlyPrice'], Provider(expected_time(7), 0.36), 7),
        (PRICES['HourlyPrice'], Provider(expected_time(9), 0.2), 9),
        (PRICES['HourlyPrice'], Provider(expected_time(12), 0.2), 12),
        (PRICES['HourlyPrice'], Provider(expected_time(13), 0.36), 37),
        (PRICES['HourlyPrice'], Provider(expected_time(21), 0.36), 45),
        (PRICES['HourlyPrice'], Provider(expected_time(22), 0.2), 22),
        (PRICES['HourlyPrice'], Provider(expected_time(23), 0.2), 23),

        (PRICES['FlatPrice'], Provider(expected_time(0), 0.5), 0),
        (PRICES['FlatPrice'], Provider(expected_time(0), 0.5), 24),
        (PRICES['FlatPrice'], Provider(expected_time(15), 0.5), 15),
        (PRICES['FlatPrice'], Provider(expected_time(15), 0.5), 38),
        
    )
)
def test_create_hourly_provider(input, expected, index, time_window):
    provider = _create_hourly_provider(input, time_window, index)

    assert provider == expected
    