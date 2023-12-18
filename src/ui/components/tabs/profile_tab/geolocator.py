"""
Class for handling geolocation of addresses

Date:
    07-11-2023

"""

from typing import Any
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut


class GeoLocator(Nominatim):
    """ Class for doing geolocation on user address """
    def __init__(self, address: str, city: str, postal_code: str, country: str):
        super().__init__(user_agent='HomeBatteryController')
        self._address = address
        self._city = city
        self._postal_code = postal_code
        self._country = country
        

    def locate(self, info: str = '') -> str | Any:
        """ Do geolocation on input address in the world. 
        Use `info` argument to specify a specific information part to retrieve.

        Args:
            info: Which information part to retrieve from geolocation

        Returns:
            Full geolocation if no input argument else only specified information part
        
        """
        try:
            location = self.geocode(f"{self._address}, {self._postal_code}, {self._city}, {self._country}")
        except (GeocoderUnavailable, GeocoderTimedOut):
            return ""
   
        if info == 'region':
            split_address = location.address.split(',') # type: ignore
            region = [string for string in split_address if 'Region' in string]
            return region[0].replace(' ', '')
        
        return location.address # type: ignore
    