"""
Class for holding parsing functions

Date:
    18-09-2023

"""

from datetime import datetime, date


class Parser:
    """ Class for parsing different types of raw data """

    @staticmethod
    def parse_spot_price(spot_price: float) -> float:
        """  Parses spot price from DKK/MWh to DKK/kwh  

        Args:
            price: Electricity spot price in DKK/MWh

        Returns:
            Electricity spot price in DKK/kwh and in 2 decimal places

        Example:
            >>> parse_price(price=779.520020)
            0.7795

        """
        return round((spot_price*0.001), 4)

    @staticmethod
    def parse_time(time: str) -> datetime:
        """ Parses EnergiDataService time string to `datetime` object

        Args:
            time: Time string from EnergiDataService dataset

        Returns:
            Time as a `datetime` object

        Example:
            >>> parse_time(time="2023-08-20T18:00:00")
            "2023-08-20 18:00:00"

        """
        return datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def parse_iso_time(time: str) -> datetime:
        """ Parses ISO 8601 formatted time string to `datetime` object

        Args:
            time: Time string in ISO 8601 format

        Returns:
            Time as a `datetime` object

        Example:
            >>> parse_time(time="2023-09-14T17:00:00.0000000Z")
            "2023-09-14 17:00:00"
    
        """
        dt = datetime.fromisoformat(time)
        return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    
    @staticmethod
    def parse_date(date_str: str) -> date:
        """ Parses date string to `date` object

        Args:
            date_str: Date string

        Returns:
            Date as a `date` object
        """
        return datetime.strptime(date_str, "%Y-%m-%d").date()
