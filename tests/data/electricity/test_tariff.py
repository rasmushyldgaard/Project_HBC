"""
Pytests for tariff.py

Date:
    10-09-2023

"""
#pylint: skip-file

import pytest
from datetime import datetime, date, timedelta

from data.electricity.tariff import Tariff, _create_hourly_tariff, _get_active_records


TARIFFS = [
    [
      { 
        'ChargeTypeCode': 'Tariff1', 'ValidFrom': '2023-07-01T00:00:00', 'ValidTo': '2024-12-12T12:00:00',
        'Price1': 0.0114, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
      {
        'ChargeTypeCode': 'Tariff2', 'ValidFrom': '2022-10-01T00:00:00', 'ValidTo': None,
        'Price1': 0.2709, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      }
    ],
    [
      { 
        'ChargeTypeCode': 'OtherTariff', 'ValidFrom': '2023-09-11T00:00:00', 'ValidTo': '2023-09-12T00:00:00',
        'Price1': 0.1509, 'Price2': 0.1509, 'Price3': 0.1509, 'Price4': 0.1509, 'Price5': 0.1509, 'Price6': 0.1509,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.5887,
        'Price19': 0.5887, 'Price20': 0.5887, 'Price21': 0.5887, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
    ],
    [
      { 
        'ChargeTypeCode': 'SomeTariff', 'ValidFrom': '2022-09-12T00:00:00', 'ValidTo': '2023-09-12T00:00:00',
        'Price1': 0.2264, 'Price2': 0.2264, 'Price3': 0.2264, 'Price4': 0.2264, 'Price5': 0.2264, 'Price6': 0.2264,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.2264,
        'Price19': 0.2264, 'Price20': 0.2264, 'Price21': 0.2264, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
    ]
]

RECORDS = [
      { 
        'ChargeTypeCode': 'Tariff', 'ValidFrom': '2023-07-01T00:00:00', 'ValidTo': '2024-12-12T12:00:00',
        'Price1': 0.0114, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
      {
        'ChargeTypeCode': 'Tariff', 'ValidFrom': '2023-10-01T00:00:00', 'ValidTo': None,
        'Price1': 0.2709, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
      { 
        'ChargeTypeCode': 'Tariff', 'ValidFrom': '2023-09-11T00:00:00', 'ValidTo': '2023-09-12T00:00:00',
        'Price1': 0.1509, 'Price2': 0.1509, 'Price3': 0.1509, 'Price4': 0.1509, 'Price5': 0.1509, 'Price6': 0.1509,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.5887,
        'Price19': 0.5887, 'Price20': 0.5887, 'Price21': 0.5887, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
      { 
        'ChargeTypeCode': 'Tariff', 'ValidFrom': '2022-09-12T00:00:00', 'ValidTo': '2023-09-12T00:00:00',
        'Price1': 0.2264, 'Price2': 0.2264, 'Price3': 0.2264, 'Price4': 0.2264, 'Price5': 0.2264, 'Price6': 0.2264,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.2264,
        'Price19': 0.2264, 'Price20': 0.2264, 'Price21': 0.2264, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
      {
        'ChargeTypeCode': 'Tariff', 'ValidFrom': '2022-10-01T00:00:00', 'ValidTo': None,
        'Price1': 0.2709, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },

]

@pytest.fixture
def tariff():
    return Tariff(datetime(2022, 12, 24, 23, 00, 00), 0.69)

@pytest.fixture
def time_window():
    todays_date = date.today()
    return (datetime(todays_date.year, todays_date.month, todays_date.day, 0, 0, 0), 
            (datetime(todays_date.year, todays_date.month, todays_date.day, 23, 00, 00) + timedelta(1)))

def expected_time(index: int) -> datetime:        
    return (date.today() + timedelta(1)) + timedelta(hours=index)

"""=========================================   TESTS   ==================================================="""

def test_tariff_class(tariff: Tariff):
    expected_time = datetime(2022, 12, 24, 23, 00, 00)
    expected_price = 0.69

    assert tariff.time == expected_time
    assert tariff.price == expected_price


def test_tariff_repr(tariff: Tariff):
    expected_str = f"Tariff(time=2022-12-24 23:00:00, price=0.69)"

    assert tariff.__repr__() == expected_str


def test_tariff_comparison(tariff: Tariff):
    tariff_1 = Tariff(datetime(2024, 8, 19, 23, 00, 00), 0)
    tariff_2 = Tariff(datetime(2022, 1, 7, 8, 00, 00), 1.20)
    tariff_3 = Tariff(datetime(2023, 12, 12, 13, 00, 00), 0.69)

    assert tariff_1 < tariff
    assert tariff_2 > tariff
    assert tariff_3 == tariff


@pytest.mark.parametrize(
    ('input', 'expected', 'index'),
    (
        (TARIFFS[0], Tariff(expected_time(0), 0.2823), 0),
        (TARIFFS[0], Tariff(expected_time(12), 0.2823), 12),
        (TARIFFS[0], Tariff(expected_time(20), 0.2823), 20),
        (TARIFFS[0], Tariff(expected_time(0), 0.2823), 24),
        (TARIFFS[0], Tariff(expected_time(12), 0.2823), 36),
        (TARIFFS[0], Tariff(expected_time(20), 0.2823), 44),
        (TARIFFS[0], Tariff(expected_time(23), 0.2823), 47),

        (TARIFFS[1], Tariff(expected_time(0), 0.1509), 0),
        (TARIFFS[1], Tariff(expected_time(9), 0.2264), 9),
        (TARIFFS[1], Tariff(expected_time(20), 0.5887), 20),
        (TARIFFS[1], Tariff(expected_time(24), 0.2264), 23),
        (TARIFFS[1], Tariff(expected_time(0), 0.1509), 24),
        (TARIFFS[1], Tariff(expected_time(9), 0.2264), 33),
        (TARIFFS[1], Tariff(expected_time(20), 0.5887), 44),
        (TARIFFS[1], Tariff(expected_time(23), 0.2264), 47),

        (TARIFFS[2], Tariff(expected_time(0), 0.2264), 0),
        (TARIFFS[2], Tariff(expected_time(12), 0.2264), 12),
        (TARIFFS[2], Tariff(expected_time(20), 0.2264), 20),
        (TARIFFS[2], Tariff(expected_time(0), 0.2264), 24),
        (TARIFFS[2], Tariff(expected_time(12), 0.2264), 36),
        (TARIFFS[2], Tariff(expected_time(20), 0.2264), 44),
        (TARIFFS[2], Tariff(expected_time(23), 0.2264), 47),

    )
)
def test_create_hourly_tariff(input, expected, index, time_window):
    tariff = _create_hourly_tariff(input, time_window, index)

    assert tariff == expected


def test_get_active_records(time_window):
    time_format = "%Y-%m-%dT%H:%M:%S"
    today = (date.today()) + timedelta(hours=0)
    yesterday = (date.today() - timedelta(1)) + timedelta(hours=0)
    future = (date.today() + timedelta(2)) + timedelta(hours=0)
    past = (date.today() - timedelta(2)) + timedelta(hours=0)
    random_records = [
      { 
        'ChargeTypeCode': 'Tariff1', 'ValidFrom': '2023-07-01T00:00:00', 'ValidTo': f'{future.strftime(time_format)}',
        'Price1': 0.0114, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
      { 
        'ChargeTypeCode': 'Tariff2', 'ValidFrom': f'{past.strftime(time_format)}', 'ValidTo': f'{past.strftime(time_format)}',
        'Price1': 0.1509, 'Price2': 0.1509, 'Price3': 0.1509, 'Price4': 0.1509, 'Price5': 0.1509, 'Price6': 0.1509,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.5887,
        'Price19': 0.5887, 'Price20': 0.5887, 'Price21': 0.5887, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
      {
        'ChargeTypeCode': 'Tariff3', 'ValidFrom': '2023-09-01T00:00:00', 'ValidTo': None,
        'Price1': 0.2709, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
      { 
        'ChargeTypeCode': 'Tariff4', 'ValidFrom': f'{past.strftime(time_format)}', 'ValidTo': f'{future.strftime(time_format)}',
        'Price1': 0.2264, 'Price2': 0.2264, 'Price3': 0.2264, 'Price4': 0.2264, 'Price5': 0.2264, 'Price6': 0.2264,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.2264,
        'Price19': 0.2264, 'Price20': 0.2264, 'Price21': 0.2264, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
      {
        'ChargeTypeCode': 'Tariff5', 'ValidFrom': '2022-10-01T00:00:00', 'ValidTo': None,
        'Price1': 0.2709, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
      { 
        'ChargeTypeCode': 'Tariff6', 'ValidFrom': f'{yesterday.strftime(time_format)}', 'ValidTo': f'{today.strftime(time_format)}',
        'Price1': 0.2264, 'Price2': 0.2264, 'Price3': 0.2264, 'Price4': 0.2264, 'Price5': 0.2264, 'Price6': 0.2264,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.2264,
        'Price19': 0.2264, 'Price20': 0.2264, 'Price21': 0.2264, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
      { 
        'ChargeTypeCode': 'Tariff7', 'ValidFrom': f'{past.strftime(time_format)}', 'ValidTo': None,
        'Price1': 0.1509, 'Price2': 0.1509, 'Price3': 0.1509, 'Price4': 0.1509, 'Price5': 0.1509, 'Price6': 0.1509,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.5887,
        'Price19': 0.5887, 'Price20': 0.5887, 'Price21': 0.5887, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
      {
        'ChargeTypeCode': 'Tariff8', 'ValidFrom': '2023-09-01T00:00:00', 'ValidTo': '2023-09-10T00:00:00',
        'Price1': 0.2709, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
      {
        'ChargeTypeCode': 'Tariff9', 'ValidFrom': f'{time_window[1].strftime(time_format)}', 'ValidTo': f'{(time_window[1] + timedelta(1)).strftime(time_format)}',
        'Price1': 0.2709, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
    ]
    expected_records = [
      { 
        'ChargeTypeCode': 'Tariff1', 'ValidFrom': '2023-07-01T00:00:00', 'ValidTo': f'{future.strftime(time_format)}',
        'Price1': 0.0114, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
      { 
        'ChargeTypeCode': 'Tariff4', 'ValidFrom': f'{past.strftime(time_format)}', 'ValidTo': f'{future.strftime(time_format)}',
        'Price1': 0.2264, 'Price2': 0.2264, 'Price3': 0.2264, 'Price4': 0.2264, 'Price5': 0.2264, 'Price6': 0.2264,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.2264,
        'Price19': 0.2264, 'Price20': 0.2264, 'Price21': 0.2264, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
      {
        'ChargeTypeCode': 'Tariff9', 'ValidFrom': f'{time_window[1].strftime(time_format)}', 'ValidTo': f'{(time_window[1] + timedelta(1)).strftime(time_format)}',
        'Price1': 0.2709, 'Price2': None, 'Price3': None, 'Price4': None, 'Price5': None, 'Price6': None,
        'Price7': None, 'Price8': None, 'Price9': None, 'Price10': None, 'Price11': None, 'Price12': None,
        'Price13': None, 'Price14': None, 'Price15': None, 'Price16': None, 'Price17': None, 'Price18': None,
        'Price19': None, 'Price20': None, 'Price21': None, 'Price22': None, 'Price23': None, 'Price24': None
      },
      { 
        'ChargeTypeCode': 'Tariff7', 'ValidFrom': f'{past.strftime(time_format)}', 'ValidTo': None,
        'Price1': 0.1509, 'Price2': 0.1509, 'Price3': 0.1509, 'Price4': 0.1509, 'Price5': 0.1509, 'Price6': 0.1509,
        'Price7': 0.2264, 'Price8': 0.2264, 'Price9': 0.2264, 'Price10': 0.2264, 'Price11': 0.2264, 'Price12': 0.2264,
        'Price13': 0.2264, 'Price14': 0.2264, 'Price15': 0.2264, 'Price16': 0.2264, 'Price17': 0.2264, 'Price18': 0.5887,
        'Price19': 0.5887, 'Price20': 0.5887, 'Price21': 0.5887, 'Price22': 0.2264, 'Price23': 0.2264, 'Price24': 0.2264
      },
    ]

    active_records = _get_active_records(random_records, time_window)

    assert active_records == expected_records