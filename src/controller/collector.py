"""
Class for collecting data from the `Data`-module and converting to DataFrames

Date:
    10-09-2023

"""

import os
import pandas as pd
from os import path
from datetime import datetime, date, timedelta 
from typing import Any

from data import Electricity, Solar, Battery, \
                 get_electricity, get_solars, get_empty_solars, get_battery
from data.helperfunctions import WeekDays


DATABASE = path.dirname(__file__).replace('controller', 'database')
CONSUMPTION_DATA = "test_data"

class Collector:
    """ Class for collecting data and converting to DataFrames """
    def __init__(self, settings: dict[str, Any], full_scope: bool = False):
        self._electricity = get_electricity(price_area=settings['price_area'],
                                            tariff_company=settings['tariff_company'],
                                            full_scope=full_scope)
        self._time_window = (self._electricity[0].time, self._electricity[-1].time)

        if settings['solcast_key'] and settings['solcast_ids']:
            self._solar = get_solars(settings['solcast_key'], 
                                     settings['solcast_ids'], 
                                     self._time_window, full_scope=full_scope)
        else:
            self._solar = get_empty_solars(self._time_window)
        
        self._battery = get_battery()
        self._expected_consumption = self._get_expected_consumption(self._time_window)
        self._data = self._convert_data_to_dataframe(self._electricity, self._solar,  self._expected_consumption)


    @property
    def electricity(self) -> list[Electricity]:
        """ Get electricity prices """
        return self._electricity
    
    @property
    def solar(self) -> list[Solar]:
        """ Get solar power estimates """
        return self._solar

    @property
    def battery(self) -> Battery:
        """ Get battery information """
        return self._battery

    @property
    def expected_consumption(self) -> pd.DataFrame:
        """ Get expected electricity consumption """
        return self._expected_consumption
    
    @property
    def data(self) -> pd.DataFrame:
        """ Get all collected data """
        return self._data
    
    @property
    def time_window(self) -> tuple[datetime, datetime]:
        """ Get the times of known electricity prices """
        return self._time_window

    def _convert_data_to_dataframe(self, 
                                   electricity: list[Electricity], 
                                   solars: list[Solar], 
                                   expected_consumption: pd.DataFrame) -> pd.DataFrame: # pragma: no cover
        """ Convert all data to a single DataFrame

        Args:
            electricity: Electricity prices
            solars: Solar power estimates
            expected_consumption: Expected electricity consumption

        Returns:
            All collected data as a single DataFrame

        """
        el = pd.DataFrame([[elec.time, elec.price] for elec in electricity])
        el.columns = ['Time', 'Price']

        sp = pd.DataFrame([[elec.spot_price.time, elec.spot_price.price] for elec in electricity])
        sp.columns = ['Time', 'SpotPrice']

        sol = pd.DataFrame([[solar.time, solar.power] for solar in solars])
        sol.columns = ['Time', 'Power']

        merged_df = pd.merge(el, sp, on='Time')
        merged_df = pd.merge(merged_df, sol, on='Time')
        merged_df = pd.merge(merged_df, expected_consumption, on='Time')

        return merged_df


    def _get_expected_consumption(self, time_window: tuple[datetime, datetime]) -> pd.DataFrame: # pragma: no cover
        """ Get expected electricity consumption

        Args:
            time_window: Start-time and end-time of the known electricity spot prices

        Returns:
            Expected electricity consumption

        """
        today = str(list({ day.name for day in WeekDays if time_window[0].weekday() == day.value })[0])
        tomorrow = str(list({ day.name for day in WeekDays if time_window[1].weekday() == day.value })[0])

        if today != tomorrow:
            if os.name == 'posix':
                today_csv = f"{DATABASE}/{CONSUMPTION_DATA}/{today}.csv"
                tomorrow_csv = f"{DATABASE}/{CONSUMPTION_DATA}/{tomorrow}.csv"
            else:
                today_csv = f"{DATABASE}\\{CONSUMPTION_DATA}\\{today}.csv"
                tomorrow_csv = f"{DATABASE}\\{CONSUMPTION_DATA}\\{tomorrow}.csv"

            today_ec = self._convert_expected_consumption_to_dataframe(today_csv, time_window[0].date())
            tomorrow_ec = self._convert_expected_consumption_to_dataframe(tomorrow_csv, time_window[1].date())
            total_ec = pd.concat([today_ec, tomorrow_ec], ignore_index=True)
        else:
            if os.name == 'posix':
                today_csv = f"{DATABASE}/{CONSUMPTION_DATA}/{today}.csv"
            else:
                today_csv = f"{DATABASE}\\{CONSUMPTION_DATA}\\{today}.csv"
            total_ec = self._convert_expected_consumption_to_dataframe(today_csv, time_window[0].date())

        ec = total_ec[total_ec['Time'] >= time_window[0]]

        return ec

    
    def _convert_expected_consumption_to_dataframe(self, csv_file_path: str, 
                                                   time: date) -> pd.DataFrame: # pragma: no cover
        """ Convert the Expected Consumption CSV file into a DataFrame

        Args:
            csv_file_path: A file path for the daily CSV file to read
            time: Date object

        Returns:
            A DataFrame representation of the Expected Consumption

        """
        ec = pd.read_csv(csv_file_path)
        ref_time = datetime(time.year, time.month, time.day, 0, 0, 0)
        times = [ref_time + timedelta(hours=index) for index in range(0, 24)]
        ec['Time'] = times
        ec = ec[['Time', 'ExpectedConsumption']]

        return ec
