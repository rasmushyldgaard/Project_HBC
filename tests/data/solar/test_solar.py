"""
Pytests for solar.py

Date:
    20-09-2023

"""
#pylint: skip-file

import pytest
import json

from os import path
from datetime import datetime, date, timedelta
from typing import Any

from data.solar.solar import Solar, _get_active_forecasts, _create_hourly_solar
from data.helperfunctions import Parser

SOLARS = [
    [
        {"pv_estimate": 0.9273, "pv_estimate10": 0.5284, "pv_estimate90": 1.1509, "period_end": "2023-09-21T11:00:00.0000000Z", "period": "PT30M"},
        {"pv_estimate": 0.8568, "pv_estimate10": 0.5023, "pv_estimate90": 1.0469, "period_end": "2023-09-21T11:30:00.0000000Z", "period": "PT30M"}
    ],
    [
        {"pv_estimate": 0, "pv_estimate10": 0, "pv_estimate90": 0, "period_end": "2023-09-21T04:00:00.0000000Z", "period": "PT30M"},
        {"pv_estimate": 0, "pv_estimate10": 0, "pv_estimate90": 0, "period_end": "2023-09-21T04:30:00.0000000Z", "period": "PT30M"}
    ],
    [
        {"pv_estimate": 0.8748, "pv_estimate10": 0.4662, "pv_estimate90": 0.9378, "period_end": "2023-09-22T12:00:00.0000000Z", "period": "PT30M"},
        {"pv_estimate": 0.7476, "pv_estimate10": 0.4399, "pv_estimate90": 0.7703, "period_end": "2023-09-22T12:30:00.0000000Z", "period": "PT30M"}
    ],
    [
        {"pv_estimate": 0.0412, "pv_estimate10": 0.0221, "pv_estimate90": 0.0472, "period_end": "2023-09-20T17:00:00.0000000Z", "period": "PT30M"},
        {"pv_estimate": 0.0074, "pv_estimate10": 0.0044, "pv_estimate90": 0.0118, "period_end": "2023-09-20T17:30:00.0000000Z", "period": "PT30M"}
    ],

]

@pytest.fixture
def time_window():
    return (datetime(2023, 9, 21, 00, 00, 00), datetime(2023, 9, 21, 23, 00, 00))

@pytest.fixture
def solar():
    solar = Solar(datetime(2023, 9, 20, 15, 00, 00), 1.420)
    return solar

"""=========================================   TESTS   ==================================================="""

def test_solar_class(solar: Solar):
    expected_time = datetime(2023, 9, 20, 15, 00, 00)
    expected_power = 1.420

    assert solar.time == expected_time
    assert solar.power == expected_power


def test_solar_repr(solar: Solar):
    expected_str = f"Solar(time=2023-09-20 15:00:00, power=1.42)"

    assert solar.__repr__() == expected_str


def test_solar_comparison(solar: Solar):
    solar_1 = Solar(datetime(2023, 9, 20, 15, 00, 00), 0.69)
    solar_2 = Solar(datetime(2024, 12, 24, 23, 00, 00), 96.9696)
    solar_3 = Solar(datetime(1996, 10, 8, 8, 00, 00), 1.420)

    assert solar_1 < solar
    assert solar_2 > solar
    assert solar_3 == solar


@pytest.mark.parametrize(
    ('input', 'expected'),
    (
        (SOLARS[0], Solar(datetime(2023, 9, 21, 11, 00, 00), 0.8921)),
        (SOLARS[1], Solar(datetime(2023, 9, 21, 4, 00, 00), 0)),
        (SOLARS[2], Solar(datetime(2023, 9, 22, 12, 00, 00), 0.8112)),
        (SOLARS[3], Solar(datetime(2023, 9, 20, 17, 00, 00), 0.0243)) 
    )
)
def test_create_hourly_solar(input, expected):
    solar = _create_hourly_solar(input)

    assert solar == expected
