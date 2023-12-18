"""
Class for solar power forecasts from Solcast Live dataset

Date:
    12-09-2023

Dataset:
    https://solcast.com/live-and-forecast

"""

import sys
import os
import json

from os import path
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from typing import Any

from data.helperfunctions import Data, get_data, Parser, URLBuilder


if os.name == 'posix':  # pragma: no cover
    DATABASE_PATH = path.dirname(__file__).replace('data', 'database').replace('/solar', '')
    ROOFTOP_PATH = f"{DATABASE_PATH}/solcast_rooftops"
else:                   # pragma: no cover
    DATABASE_PATH = path.dirname(__file__).replace('data', 'database').replace('\\solar', '')
    ROOFTOP_PATH = f"{DATABASE_PATH}\\solcast_rooftops"

URL = { 
    'base': 'https://api.solcast.com.au',
    'params': {
        'rooftop_sites': ' ',
        '': '',
        'forecasts': ' ', 
        'format': 'json',
        'api_key': '',
    },
    'delimiters': [('/'), ('', '/'), ('', '/'), ('', '?'), ('=', '&'), ('=', '')]
}

@dataclass(frozen=True, order=True)
class Solar:
    """ Class for storing a single solar power estimate """
    _time: datetime = field(compare=False)
    _power: float

    def __repr__(self):
        return f"Solar(time={self._time}, power={self._power})"
    
    @property
    def time(self) -> datetime:
        """ Get time for Solar """
        return self._time
    
    @property
    def power(self) -> float:
        """ Get power for Solar """
        return self._power


def get_solars(api_key: str, 
               resource_ids: list[str], 
               time_window: tuple[datetime, datetime],
               full_scope: bool = False) -> list[Solar]: # pragma: no cover
    """ Loops over rooftop resource ID's to collect and compute multiple Solcast rooftop forecasts

    Args:
        api_key: Solcast API access key
        resource_ids: ID's for Solcast rooftops
        time_window: Start-time and end-time of the known electricity spot prices

    Returns:
        A list of `Solar` objects
    """
    solars = []
    
    for resource_id in resource_ids:
        solars.append(_get_solar(api_key, resource_id, time_window, full_scope))

    if len(solars) > 1:
        # If there is more than 1 rooftop, we need to add all the Solar objects to a total Solar object
        grouped_solars = zip(*solars)
        solars = [Solar(solar[0].time, sum(sol.power for sol in solar)) for solar in grouped_solars] # type: ignore
    else:
        solars = solars[0]  # type: ignore

    return solars # type: ignore


def get_empty_solars(time_window: tuple[datetime, datetime]) -> list[Solar]: # pragma: no cover
    """ Get a list of empty solar power

    Args:
        time_window: Start-time and end-time of the known electricity spot prices

    Returns:
        A list of empty `Solar` objects for every hour in time_window

    """
    solars = []
    hour_diff = int(divmod(abs((time_window[1] - time_window[0]).total_seconds()), 3600)[0]) + 1
    start_index = time_window[0].hour

    for index in range(start_index, start_index+hour_diff):
        next_day = False

        if index >= 24:
            index -= 24
            next_day = True

        if next_day:
            time = time_window[1].replace(hour=index)
        else:
            time = time_window[0].replace(hour=index)

        solars.append(Solar(time, 0))

    return solars


def _get_solar(api_key: str, 
               resource_id: str, 
               time_window: tuple[datetime, datetime],
               full_scope: bool = False) -> list[Solar]: # pragma: no cover
    """ Get solar power estimate forecasts from a single Solcast 

    Args:
        api_key: Solcast API access key
        resource_id: ID of Solcast rooftop
        time_window: Start-time and end-time of the known electricity spot prices

    Returns:
        A list of `Solar` objects

    """
    solar_forecasts = _forecasts_exists_and_active(resource_id)

    if not solar_forecasts:
        # If the saved data is outdated, get new data from Solcast
        url = URLBuilder.set_values(URL, values=[resource_id, api_key])
        solar_data = get_data(URLBuilder(url).url)

        if solar_data.status_code != 200:
            # TODO: Better error handling.
            print(f"(Solar Forecasts) Error! Status Code: {solar_data.status_code}")
            sys.exit(1)

        _save_solcast_data(resource_id, solar_data, folder="forecasts")
        solar_forecasts = solar_data.json['forecasts']

    if full_scope:
        solar_live = _estimated_actuals_exists_and_active(resource_id)

        if not solar_live:
            url = URLBuilder.set_params(URL, 
                                        params=[('forecasts', 'estimated_actuals')])
            url = URLBuilder.set_values(url, values=[resource_id, api_key])
            solar_data = get_data(URLBuilder(url).url)

            if solar_data.status_code != 200:
                # TODO: Better error handling.
                print(f"(Solar Live) Error! Status Code: {solar_data.status_code}")
                sys.exit(1)

            _save_solcast_data(resource_id, solar_data, folder="estimated_actuals")
            solar_live = solar_data.json['estimated_actuals']
        
        relevant_forecasts = _get_active_and_past_forecasts(solar_forecasts, solar_live, time_window)
    else:
        relevant_forecasts = _get_active_forecasts(solar_forecasts, time_window)
    
    solars = []
    for index in range(0, len(relevant_forecasts), 2):
        forecasts = relevant_forecasts[index:index+2]
        solar = _create_hourly_solar(forecasts)
        solars.append(solar)

    return solars


def _create_hourly_solar(forecasts: list[dict[str, Any]]) -> Solar:
    """ Create a Solar object for a specific hour of the day

    Args:
        forecasts: Solar power estimate forecasts
    
    Returns:
        A `Solar` object

    """
    time = Parser.parse_iso_time(forecasts[0]['period_end'])
    power = (forecasts[0]['pv_estimate'] + forecasts[1]['pv_estimate']) / 2

    return Solar(time, round(power, 4))
    

def _get_active_forecasts(forecasts: list[dict[str, Any]], 
                          time_window: tuple[datetime, datetime]) -> list[dict[str, Any]]: # pragma: no cover
    """ Search through solar forecasts from Solcast and find the present forecasts

    Args:
        forecasts: Solar power estimate forecasts
        time_window: Start-time and end-time of the known electricity spot prices

    Returns:
        A list of solar power estimate forecasts within the time window

    """
    active_forecasts = []

    for forecast in forecasts:
        if Parser.parse_iso_time(forecast['period_end']) >= time_window[0] and \
           Parser.parse_iso_time(forecast['period_end']) <= (time_window[1] + timedelta(minutes=30)):
            active_forecasts.append(forecast)

    return active_forecasts


def _get_active_and_past_forecasts(active_forecasts: list[dict[str, Any]],
                                   past_forecasts: list[dict[str, Any]],
                                   time_window: tuple[datetime, datetime]) -> list[dict[str, Any]]: # pragma: no cover
    """ Searches through solar forecasts from Solcast and finds both past and present forecasts

    Args:
        active_forecasts: Solar power estimate forecasts for the present/future
        past_forecasts: Solar power estimate forecasts from the past
        time_window: Start-time and end-time of the known electricity spot prices

    Returns:
        A list of solar power estimate forecasts within the time window

    """
    forecasts = []

    if Parser.parse_iso_time(active_forecasts[0]['period_end']).minute == 30:
        cut_time = Parser.parse_iso_time(active_forecasts[1]['period_end'])
        index = 1
    else:
        cut_time = Parser.parse_iso_time(active_forecasts[0]['period_end'])
        index = 0

    for past_forecast in past_forecasts:
        if Parser.parse_iso_time(past_forecast['period_end']) >= time_window[0] and \
           Parser.parse_iso_time(past_forecast['period_end']) < cut_time:
            forecasts.append(past_forecast)

    # Past forecasts are in reverse order compared to active forecasts.
    forecasts.reverse()

    for active_forecast in active_forecasts[index:]:
        if Parser.parse_iso_time(active_forecast['period_end']) >= cut_time and \
           Parser.parse_iso_time(active_forecast['period_end']) <= (time_window[1] + timedelta(minutes=30)):
            forecasts.append(active_forecast)

    return forecasts

        
def _forecasts_exists_and_active(resource_id: str) -> Any: # pragma: no cover
    """ Checks if a Solcast JSON file of the "forecasts" dataset exists and is active.
        If file exists, load data from the file, else return an empty list

    Args:
        resource_id: ID of Solcast rooftop

    Returns:
        A list with Solcast forecasts or empty list if no active file
    
    """
    todays_date = date.today()

    if os.name == 'posix':
        forecasts_folder = f"{ROOFTOP_PATH}/{resource_id}/forecasts"
    else:
        forecasts_folder = f"{ROOFTOP_PATH}\\{resource_id}\\forecasts"
    forecasts_files = [file for file in os.listdir(forecasts_folder) if not file == "dummy.json"]

    for file in forecasts_files:
        file_date = Parser.parse_date(file.split('.')[0])

        if file_date == todays_date:
            if os.name == 'posix':
                file_path = f"{forecasts_folder}/{file}"
            else:
                file_path = f"{forecasts_folder}\\{file}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                solar_forecasts = json.loads(f.read())

            return solar_forecasts['forecasts']
    
    return []


def _estimated_actuals_exists_and_active(resource_id: str) -> Any: # pragma: no cover
    """ Checks if a Solcast JSON file of the "estimated_actuals" dataset exists and is active.
        If file exists, load data from the file, else return an empty list

    Args:
        resource_id: ID of Solcast rooftop

    Returns:
        A list with Solcast forecasts or empty list if no active files

    """
    todays_date = date.today()

    if os.name == 'posix':
        estimated_actuals_folder = f"{ROOFTOP_PATH}/{resource_id}/estimated_actuals"
    else:
        estimated_actuals_folder = f"{ROOFTOP_PATH}\\{resource_id}\\estimated_actuals"
    estimated_actuals_files = [file for file in os.listdir(estimated_actuals_folder) if not file == "dummy.json"]

    for file in estimated_actuals_files:
        file_date = Parser.parse_date(file.split('.')[0])

        if file_date == todays_date:
            if os.name == 'posix':
                file_path = f"{estimated_actuals_folder}/{file}"
            else:
                file_path = f"{estimated_actuals_folder}\\{file}"

            with open(file_path, 'r', encoding='utf-8') as f:
                solar_live = json.loads(f.read())

            return solar_live['estimated_actuals']
    
    return []


def _save_solcast_data(resource_id: str, solar_data: Data, folder: str) -> None: # pragma: no cover
    """ Saves the collected Solcast forecasts into a new JSON file for reuse

    Args:
        resource_id: ID of Solcast rooftop
        solar_data: Solcast response content
    
    """
    todays_date = date.today()

    if os.name == 'posix':
        rooftop_folder = f"{ROOFTOP_PATH}/{resource_id}/{folder}"
        new_rooftop_file = f"{rooftop_folder}/{todays_date}.json"
    else:
        rooftop_folder = f"{ROOFTOP_PATH}\\{resource_id}\\{folder}"
        new_rooftop_file = f"{rooftop_folder}\\{todays_date}.json"

    with open(new_rooftop_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(solar_data.json))
