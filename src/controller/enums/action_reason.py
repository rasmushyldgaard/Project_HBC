"""
Enum for the reasonings behind given actions

Date:
    06-11-2023

"""

from enum import unique, StrEnum

@unique
class ActionReason(StrEnum):
    """ Enum to explain reason for taking certain action  """
    IDLE = "Waiting For Next Action"
    IDLE_DEFAULT = "No Cheap Power Or High Consumption"
    IDLE_SOLAR_OVERFLOW = "Selling Excess SolPower"
    IDLE_SOLAR_SELL_HIGH_BUY_LOW = "Selling SolPower At High SpotPrice"
    EQUALIZE_USE_BATTERY = "Equalizing With Cheap Power"
    EQUALIZE_SOLAR_CHARGE = "Charging Expected SolPower Surplus"
    CHARGE_LATER_CONSUMPTION = "Charging Cheap GridPower"
