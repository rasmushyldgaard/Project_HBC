""" Enum class for the variable names in MiniCon"""

from enum import StrEnum

class MiniConVariable(StrEnum):
    """ Enums of the variables used in MiniCon battery system """
    SOC = '"VA_MC02_BatteryGroup1StateOfChargeOfDischargeAvailablePacks"'
    BATTERY_LEVEL = '"VA_String_02_Remaining_Charge"'
    HOUSE_NET_RATE = '"VA_NetChargeRate"'
    REFERENCE_CURRENT1 = '"VA_MC01_OperationRequestsDCModeCurrentReference"'
    REFERENCE_CURRENT = '"VA_MC02_OperationRequestsDCModeCurrentReference"'