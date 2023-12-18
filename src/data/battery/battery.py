"""
Class for holding state of charge and real consumption for battery system

Date:
    06-11-2023

"""

from datetime import datetime
from dataclasses import dataclass

from data.helperfunctions.minicon import MiniCon, MiniConVariable


PORT = '/dev/ttyUSB0'
ACTIONS = {
    'idle': 0,
    'charge': -12,
}

@dataclass(frozen=True)
class Battery:
    """ Class for storing battery system information """
    _time: datetime
    _soc: float
    _real_consumption: float

    def __repr__(self):
        return f"Battery(time={self._time}, soc={self._soc})"
    
    @property
    def time(self) -> datetime:
        """ Get time for Battery """
        return self._time
    
    @property
    def soc(self) -> float:
        """ Get state of charge for Battery """
        return self._soc
    
    @property
    def real_consumption(self) -> float:
        """ Get current real consumption for Battery """
        return self._real_consumption


def get_battery(port: str = PORT) -> Battery:
    """ Get a Battery object with current state of charge and real consumption

    Args:
        port: Serial port for communication

    Returns:
        Battery object with time, state of charge and real consumption
        
    """
    minicon = MiniCon(port)
    soc = minicon.get_value(MiniConVariable.SOC)
    real_cons = minicon.get_value(MiniConVariable.HOUSE_NET_RATE)

    return Battery(datetime.now(), float(soc), float(real_cons))


def set_battery(value: str, port: str = PORT) -> None:
    """ Set a value in active battery system 
    
    Args:
        value: The value to set
        port: Serial port for communication

    """
    minicon = MiniCon(port)

    if value == 'equalize':
        minicon.set_variable_to_manual(MiniConVariable.REFERENCE_CURRENT, False)
    else:
        minicon.set_variable_to_manual(MiniConVariable.REFERENCE_CURRENT, True)
        test = minicon.set_value(MiniConVariable.REFERENCE_CURRENT, ACTIONS[value])
        print(test)

    
    
