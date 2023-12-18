""" 
MiniCon class is supposed to start a serial connection to MiniCon and allow to get values
from MiniCon and set values in MiniCon. 

Get values for battery level and consumption for controller and saving for expected consumption.
Set values for reference current to idle or charge! 

Date:
    10-11-2023

"""

import serial
from typing import Any

from .minicon_variable import MiniConVariable


BAUDRATE = 115200
TIMEOUT = 1
RETRIES = 3

class MiniCon():
    """ Class to communicate with MiniCon battery system """
    def __init__(self, port: str):
        self._port = port
    
    def get_value(self, var: MiniConVariable) -> str:
        """ Get a value from specified MiniCon variable
            
        Args:
            var: MiniCon variable to get value from

        Returns:
            The specified variable value

        """
        command = f'var_ShowValue {var.value}'
        response = self._send_and_receive(command)
        return self._filter_get_response(command, response)

    
    def set_value(self, var: MiniConVariable, value: Any) -> bool:
        """ Set a value for a specified MiniCon variable

        Args:
            var: MiniCon variable to set
            value: The value to set

        Returns:
            True/False if value was set or not in MiniCon
        
        """
        command = f'var_DebSetVarByName {var.value} "{value}"'
        response = self._send_and_receive(command)
        return self._verify_set_response(command, response, value)
    

    def set_variable_to_manual(self, var: MiniConVariable, manual: bool) -> bool:
        """ Set a variable in MiniCon for manual control

        Args:
            var: MiniCon variable to set
            manual: True/False for manual or automatic control

        Returns:
            True/False if manual control was set?
        
        """
        command = f'SC var_DebSetVarManualByName {var.value} "{int(manual)}"'
        _ = self._send_and_receive(command)
        return True  # TODO: Don't have to `verify` response?


    def _send_and_receive(self, command: str) -> str:
        """ Send request and receive response from MiniCon

        Args:
            command: The MiniCon command string to send

        Returns:
            MiniCon response

        """
        request = f"{command} \n".encode("utf-8")

        for _ in range(RETRIES):
            response = ""

            with serial.Serial(self._port, BAUDRATE, timeout=TIMEOUT, write_timeout=TIMEOUT) as ser:
                ser.write(request)
                ser.read_until(b'#')
            
            if not response:
                continue
            return response.decode(encoding='utf-8') # type: ignore
        return ""   # TODO: If an empty string was returned after 3 retries,
                    #       we could "log" an error and handle it in upper layer.


    def _filter_get_response(self, command: str, response: str) -> str:
        """ Filtering of a get_value response

        Args:
            command: The MiniCon command string to send
            response: Response string from MiniCon

        Returns:
            The actual get_value response

        """
        if command in response:
            start = response.find('\n') + 1
            end = response.find('\n', start) - 1
            value = response[start:end]
        else:
            value = response
        return value
    

    def _verify_set_response(self, command: str, response: str, value: Any) -> bool:
        """ Verify that the correct value was set in a set_value response

        Args:
            command: The MiniCon command string to send
            response: Response string from MiniCon
            value: The value to set in MiniCon

        Returns:
            True/False if correct value was set or not

        """
        if command in response:
            start = response.find('string')
            start = response.find(' ', start) + 1
            end = response.find('\n', start) - 1
            
            if value == float(response[start:end]):
                return True
        return False

    