"""
Class for electricity tariffs from EnergiDataService

Date:
    08-09-2023

Dataset:
    https://www.energidataservice.dk/tso-electricity/DatahubPricelist

"""

import sys
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any

from data.helperfunctions import get_data, Parser, URLBuilder
from data.electricity.tariff_company import TARIFF_COMPANY


TARIFF_AMOUNT = 24
URL = {
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
}


@dataclass(frozen=True, order=True)
class Tariff:
    """ Class for storing a single electricity tariff """
    _time: datetime = field(compare=False)
    _price: float

    def __repr__(self):
        return f"Tariff(time={self._time}, price={self._price})"
    
    @property
    def time(self) -> datetime:
        """ Get time for Tariff """
        return self._time
    
    @property
    def price(self) -> float:
        """ Get price for Tariff (DKK/kWh) """
        return self._price
    

def get_tariffs(company: str, time_window: tuple[datetime, datetime]) -> list[Tariff]: # pragma: no cover
    """ Get tariffs for the specified Tariff Company from EnergiDataService DataHub dataset

    Args:
        company: The local electricity tariff company
        time_window: Start-time and end-time of the known electricity spot prices

    Returns:
        A list of Tariff objects
        
    """
    gln = TARIFF_COMPANY[company]["gln"]
    charge_type_codes = TARIFF_COMPANY[company]["type"]
    codes = f'{list(charge_type_codes)}'
    codes = codes.replace("'", '"')

    filter1 = f'"GLN_Number":["{gln}"]'
    filter2 = f'"ChargeTypeCode":{codes}'
    filtering = '{' + filter1 + ',' + filter2 + '}'
    url = URLBuilder.set_values(URL, values=[f"{time_window[1].date()}", filtering])

    tariff_data = get_data(URLBuilder(url).url)

    if tariff_data.status_code != 200:
        # TODO: Better error handling.
        print(f"Error! Status Code: {tariff_data.status_code}")
        sys.exit(1)

    dataset_records = tariff_data.json['records']
    active_records = _get_active_records(dataset_records, time_window)
    hour_diff = int(divmod(abs((time_window[1] - time_window[0]).total_seconds()), 3600)[0]) + 1
    start_index = time_window[0].hour
    tariffs = [_create_hourly_tariff(active_records, time_window, index) 
               for index in range(start_index, start_index+hour_diff)]

    return tariffs


def _create_hourly_tariff(active_records: list[dict[str, Any]], 
                          time_window: tuple[datetime, datetime],
                          index: int) -> Tariff:
    """ Create a Tariff object for a specific hour of the day

    Args:
        active_records: The tariff prices for the present
        time_window: Start-time and end-time of the known electricity spot prices
        index: Current hour count

    Returns:
        A Tariff object

    """
    next_day = False
    if index >= 24:
        index -= 24
        next_day = True

    price_key = f"Price{index+1}"

    if next_day:
        time = time_window[1].replace(hour=index)
    else:
        time = time_window[0].replace(hour=index)

    price = 0
    for active_record in active_records:
        if active_record[price_key] is not None:
            price += active_record[price_key]
        else:
            price += active_record["Price1"]
            
    return Tariff(time, price)


def _get_active_records(records: list[dict[str, Any]], time_window: tuple[datetime, datetime]) -> list[dict[str, Any]]:
    """ Search through tariff records from EnergiDataService and find the present records

    Args:
        records: The tariff records from EnergiDataService
        tomorrow: Date of tomorrow

    Returns:
        A list of present tariff records

    """
    active_records = []
    latest_active_record_with_no_expiration = {}
    current_diff_in_dates = 0
    first_record_with_no_expiration = True
    
    for record in records: # pylint: disable=too-many-nested-blocks
        record_valid_from_date = Parser.parse_time(record["ValidFrom"]).date()

        if record["ValidTo"] is not None:
            record_valid_to_date = Parser.parse_time(record["ValidTo"]).date()

            if record_valid_from_date == time_window[1].date():
                active_records.append(record)
            elif record_valid_from_date <= time_window[0].date() and record_valid_to_date >= time_window[1].date():
                # Check if we already appended a record with same ChargeTypeCode
                # and make sure that we ONLY get the record with latest ValidFrom date!
                if active_records:
                    if record["ChargeTypeCode"] != active_records[-1]["ChargeTypeCode"]: # pragma: no cover
                        active_records.append(record)
                    else:
                        if record_valid_from_date > \
                            Parser.parse_time(active_records[-1]["ValidFrom"]).date(): # pragma: no cover
                            _ = active_records.pop(-1)
                            active_records.append(record)
                else:
                    active_records.append(record)

        else:
            # Incase there are multiple records with "ValidTo" = null,
            # Let's make sure that we get the actual latest record.
            if record_valid_from_date <= time_window[1].date():
                diff_in_dates = abs((time_window[0].date() - record_valid_from_date).days)

                # Take the first record with no expiration as reference!
                if first_record_with_no_expiration:
                    current_diff_in_dates = diff_in_dates
                    first_record_with_no_expiration = False
                    latest_active_record_with_no_expiration = record
            
                if diff_in_dates < current_diff_in_dates:
                    latest_active_record_with_no_expiration = record

    if latest_active_record_with_no_expiration:
        active_records.append(latest_active_record_with_no_expiration)

    return active_records
