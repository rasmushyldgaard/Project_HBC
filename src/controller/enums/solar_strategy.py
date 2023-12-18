"""
Enum for the reasonings behind given actions

Date:
    06-11-2023

"""

from enum import unique, StrEnum

@unique
class SolarStrategy(StrEnum):
    """ Enum for which strategy to take on solar power surplus """
    SELL_ALL = "Sell All"
    SAVE_ALL = "Save All"