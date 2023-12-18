"""
Class for electricity spot prices from EnergiDataService

Date:
    19-08-2022

Dataset:
    https://www.energidataservice.dk/tso-electricity/elspotprices

"""

import sys
from datetime import datetime, date
from dataclasses import dataclass, field

from data.helperfunctions import get_data, Parser, URLBuilder


URL = {
    'base': 'https://api.energidataservice.dk/dataset/Elspotprices',
    'params': {
        'offset': '0',
        'start': '',
        'columns': '"HourDK","PriceArea","SpotPriceDKK"',
        'filter': '',
        'sort': 'HourDK%20ASC'
    },
    'delimiters': [('?'), ('=', '&'), ('=', '&'), ('=', '&'), ('=', '&'), ('=', '')]
}

@dataclass(frozen=True, order=True)
class SpotPrice:
    """ Class for storing a single electricity spot price """
    _time: datetime = field(compare=False)
    _price_area: str = field(compare=False)
    _price: float

    def __repr__(self):
        return f"SpotPrice(time={self._time}, price_area={self._price_area}, price={self._price})"
    
    @property
    def time(self) -> datetime:
        """ Get time for SpotPrice """
        return self._time
    
    @property
    def price_area(self) -> str:
        """ Get price_area for SpotPrice (DK1 or DK2) """
        return self._price_area
    
    @property
    def price(self) -> float:
        """ Get price for SpotPrice (DKK/kWh) """
        return self._price


def get_spot_prices(price_area: str, full_scope: bool = False) -> list[SpotPrice]: # pragma: no cover
    """ Get electricity spot prices from EnergiDataService Elspotprices dataset  
    
    Args:
        price_area: DK1 (West of Great Belt) or DK2 (East of Great Belt)

    Returns:
        List of SpotPrices for the specified price_area
    
    """
    filter1 = f'"PriceArea":["{price_area}"]'
    filtering = '{' + filter1 + '}'
    url = URLBuilder.set_values(URL, values=[f"{date.today()}", filtering])
    spot_price_data = get_data(URLBuilder(url).url)

    if spot_price_data.status_code != 200:
        # TODO: Better error handling.
        print(f"Error! Status Code: {spot_price_data.status_code}")
        sys.exit(1)

    dataset_records = spot_price_data.json['records']

    if full_scope:
        spot_prices = [SpotPrice(Parser.parse_time(data['HourDK']), 
                                data['PriceArea'], 
                                Parser.parse_spot_price(data['SpotPriceDKK'])) 
                                for data in dataset_records]
    else:
        current_time = datetime.now()
        spot_prices = [SpotPrice(Parser.parse_time(data['HourDK']), 
                                data['PriceArea'], 
                                Parser.parse_spot_price(data['SpotPriceDKK'])) 
                                for data in dataset_records if Parser.parse_time(data['HourDK']) > current_time]

    return spot_prices
    