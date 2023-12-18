"""
Class for electricity provider prices

Date:
    24-08-2022

"""

from datetime import datetime, time
from dataclasses import dataclass, field

from data.electricity.provider_company import PROVIDER_COMPANY


@dataclass(frozen=True, order=True)
class Provider:
    """ Class for storing an electricity provider price """
    _time: datetime = field(compare=False)
    _price: float

    def __repr__(self):
        return f"Provider(time={self._time}, price={self._price})"
    
    @property
    def time(self) -> datetime:
        """ Get time for Provider """
        return self._time
    
    @property
    def price(self) -> float:
        """ Get price for Provider """
        return self._price
    

def get_providers(company: str, time_window: tuple[datetime, datetime]) -> list[Provider]: # pragma: no cover
    """ Get electricity provider costs for the specified company

    Args:
        company: Electricity provider company
        time_window: Start-time and end-time of the known electricity spot prices

    Returns:
        A list of Provider objects

    """
    provider_company = PROVIDER_COMPANY[company]
    provider_prices = provider_company["Price"]

    hour_diff = int(divmod(abs((time_window[1] - time_window[0]).total_seconds()), 3600)[0]) + 1
    start_index = time_window[0].hour
    providers = [_create_hourly_provider(provider_prices, time_window, index)
                 for index in range(start_index, start_index+hour_diff)]
    
    return providers


def _create_hourly_provider(prices: dict[time, float], 
                            time_window: tuple[datetime, datetime],
                            index: int) -> Provider:
    """ Create a Provider object for a specific hour of the day

    Args:
        prices: Electricity provider prices (flat or hourly)
        time_window: Start-time and end-time of the known electricity spot prices
        index: Current hour count

    Returns:
        A Provider object

    """
    next_day = False
    if index >= 24:
        index -= 24
        next_day = True

    if next_day:
        time = time_window[1].replace(hour=index) # pylint: disable=redefined-outer-name
    else:
        time = time_window[0].replace(hour=index)

    provider_price = 0.0
    for price_time in prices:
        if time.time() < price_time:
            provider_price = prices[price_time]
            break
        continue

    return Provider(time, provider_price)
