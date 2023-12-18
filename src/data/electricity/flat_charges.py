"""
Class for holding the flat electricity charges: `Government Charge`, `System Tariff` and `Transmissions Tariff`.

Date:
    10-09-2023

"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FlatCharges:
    """ Class for storing the flat electricity charges """
    _gov_charge: float = field(default=0.697)
    _sys_tariff: float = field(default=0.054)
    _trans_tariff: float = field(default=0.058)

    def __repr__(self):
        return f"FlatCharges(gov={self._gov_charge}, sys={self._sys_tariff}, trans={self._trans_tariff})"

    @property
    def gov_charge(self) -> float:
        """ Get the `Government Charge` of 0.697 DKK """
        return self._gov_charge
    
    @property
    def sys_tariff(self) -> float:
        """ Get the `System Tariff` of 0.054 DKK """
        return self._sys_tariff
    
    @property
    def trans_tariff(self) -> float:
        """ Get the `Transmissions Tariff` of 0.058 DKK """
        return self._trans_tariff
    
    @property
    def total(self) -> float:
        """ Returns the total sum of all flat electricity charges """
        return self.gov_charge + self.sys_tariff + self.trans_tariff
