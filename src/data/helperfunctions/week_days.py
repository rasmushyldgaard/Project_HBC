""" Enum for mapping python datetime to day of the week

Date:
    04-10-2023
    
"""
# pylint: skip-file

from enum import Enum, unique

@unique
class WeekDays(Enum):
    """ Enum for days of the week as integers """
    mon = 0
    tue = 1
    wed = 2
    thu = 3
    fri = 4
    sat = 5
    sun = 6
