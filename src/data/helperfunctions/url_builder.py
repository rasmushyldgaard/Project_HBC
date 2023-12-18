"""
Class for building API URL's to request

Date:
    23-09-2023

"""

import copy
from typing import Any

class URLBuilder:
    """ Builds API URL to request data from """
    def __init__(self, components: dict[str, Any]):
        self._url = self._build(components)
        
    def __repr__(self):
        return f"URLBuilder(url={self._url})"

    @property
    def url(self) -> str:
        """ Get the built URL """
        return self._url
    
    @staticmethod
    def set_params(components: dict[str, Any], params: list[tuple[str, str]]) -> dict[str, Any]: # pragma: no cover
        """ Sets the keys of params to match input params

        Args:
            components: The components which comprises the URL.
                        Includes parameters, values and delimiters.
            params: Params to be set

        Returns:
            New URL with changed params to match input params
            
        """
        new_url = copy.deepcopy(components)
        new_params = []
        index = 0
        for key in new_url["params"].items():
            for param in params:
                index += 1
                if key[0] == param[0]:
                    new_params.append(param[1])
                    index = 0
                    break

            if index > 0:
                new_params.append(key[0])

        new_url["params"] = dict(zip(new_params, list(new_url["params"].values())))
        return new_url
    

    @staticmethod
    def set_values(components: dict[str, Any], values: list[str]) -> dict[str, Any]: # pragma: no cover
        """ Sets the values of params to match input values

        Args:
            components: The components which comprises the URL.
                        Includes parameters, values and delimiters.
            values: Values to be set

        Returns:
            New URL with changed values to match input values
        
        """
        new_url = copy.deepcopy(components)
        index = 0
        for (param, value) in new_url["params"].items():
            if not value:
                new_url["params"][param] = values[index]
                index += 1
            else:
                new_url["params"][param] = value

        return new_url


    def _build(self, components: dict[str, Any]) -> str:
        """ Builds URL from URL components

        Args:
            components: The components which comprises the URL.
                        Includes parameters, values and delimiters.

        Returns:
            Built URL string

        """
        url = f"{components['base']}"
        url += components['delimiters'][0][0]

        for (param, value), delimiter in zip(components['params'].items(), components['delimiters'][1:]):
            if delimiter[0]:
                url += f"{param}{delimiter[0]}{value}"
            else:
                url += f"{param}{value.replace(' ', '')}"
            
            if delimiter[1]:
                url += delimiter[1]

        return url
