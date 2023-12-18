"""
Class for combining a SpotPrice, Tariff and FlatCharges to an abstract `Electricity`

Date:
    10-09-2023

"""

import sys
from datetime import datetime
from dataclasses import dataclass, field
from traceback import print_exc

from data.electricity.spot_price import SpotPrice, get_spot_prices
from data.electricity.tariff import Tariff, get_tariffs
from data.electricity.provider import Provider, get_providers
from data.electricity.flat_charges import FlatCharges


@dataclass(frozen=False, order=True)
class Electricity:
    """ Class for storing a single electricity """
    _time: datetime = field(init=False, compare=False)
    _price: float = field(init=False)
    _spot_price: SpotPrice = field(compare=False)
    _tariff: Tariff = field(compare=False)
    _provider: Provider = field(compare=False)
    _flat_charges: FlatCharges = field(default=FlatCharges(), compare=False)

    def __post_init__(self) -> None:
        self._time = self._tariff.time
        self._price = self._total_pricing()

    def __repr__(self):
        return f"Electricity(time={self._time}, price={self._price})"

    @property
    def time(self) -> datetime:
        """ Get time for Electricity """
        return self._time
    
    @property
    def price(self) -> float:
        """ Get price for Electricity (DKK/kWh) """
        return self._price
    
    @property
    def spot_price(self) -> SpotPrice:
        """ Get SpotPrice object for Electricity """
        return self._spot_price
    
    @property
    def tariff(self) -> Tariff:
        """ Get Tariff object for Electricity """
        return self._tariff
    
    @property
    def provider(self) -> Provider:
        """ Get Provider object for Electricity """
        return self._provider
    
    @property
    def flat_charges(self) -> FlatCharges:
        """ Get FlatCharges object for Electricity """
        return self._flat_charges
    
    def _total_pricing(self) -> float:
        """ Calculate the total pricing for a single Electricity """
        return round((self.spot_price.price + self.tariff.price + \
                      self.provider.price + self.flat_charges.total)*1.25, 4)


def get_electricity(price_area: str = "DK1", 
                    tariff_company: str = "Ikast El Net A/S",
                    provider_company: str = "Vindstød",
                    full_scope: bool = False) -> list[Electricity]: # pragma: no cover
    """ Get a list of abstract Electricity objects combined of SpotPrices and Tariffs

    Args:
        price_area: DK1 (West of Great Belt) and DK2 (East of Great Belt)
        company: The local electricity tariff company

    Returns:
        List of Electricity objects for tomorrow's electricity prices

    """
    try:
        spot_prices = get_spot_prices(price_area, full_scope)
        time_window = (spot_prices[0].time, spot_prices[-1].time)
        tariffs = get_tariffs(tariff_company, time_window)
        providers = get_providers(provider_company, time_window)

    except Exception:   # pylint: disable=broad-exception-caught
        # TODO: Better error handling.
        print_exc()
        sys.exit(1)

    electricity = [Electricity(spot_price, tariff, provider) 
                   for spot_price, tariff, provider in zip(spot_prices, tariffs, providers)]
    return electricity
