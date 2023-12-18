"""
Class for profit calculation based on input data and generated charging plan

Date:
    18-10-2023

"""
# pylint: skip-file

import pandas as pd


class Profit:
    """ Class for calculating system profit """
    def __init__(self, data: pd.DataFrame, plan: pd.DataFrame):
        self._data = data
        self._plan = plan

    @property
    def current_profit(self) -> float:
        """ Get current profit for system """
        return self._calculate_current_profit(self._data, self._plan)

    @property
    def expected_profit(self) -> float:
        """ Get expected profit for system """
        return self._calculate_expected_profit(self._data, self._plan)
    
    def calculate_total_profit(self) -> float:
        """ Calculate total profit """
        # TODO
        return 0.0


    def _calculate_current_profit(self, data: pd.DataFrame, plan: pd.DataFrame) -> float:
        """ Calculate current profit """
        # TODO
        return 0.0


    def _calculate_expected_profit(self, data: pd.DataFrame, plan: pd.DataFrame) -> float:
        """ Calculate expected profit based on planned action

        Args:
            data: Input data to Planner
            plan: Generated 

        Returns:
            Profit for current action and hour in comparison to NormalBuy

        """
        action = plan.at[0, "Action"]
        normal_buy = data.at[0, "ExpectedConsumption"] * data.at[0, "Price"]
        smart_buy = 0

        if action == 'idle':
            if plan.at[0, "SolarSurplus"] > 0:
                if not data.at[0, "SpotPrice"] <= 0:
                    smart_buy = data.at[0, "SpotPrice"] * plan.at[0, "SolarSurplus"]
            elif plan.at[0, "SolarSurplus"] < 0:
                smart_buy = data.at[0, "Price"] * abs(plan.at[0, "SolarSurplus"])

        elif action == 'charge':
            if plan.at[0, "SolarSurplus"] < 0:
                smart_buy = data.at[0, "Price"] * abs(plan.at[0, "SolarSurplus"])
                smart_buy += data.at[0, "Price"] * plan.at[0, "ElNetCharge"]
            elif plan.at[0, "SolarSurplus"] >= 0 and plan.at[0, "SolarSurplus"] < 3:
                smart_buy = data.at[0, "Price"] * plan.at[0, "ElNetCharge"]
            elif plan.at[0, "SolarSurplus"] > 3:
                if not data.at[0, "SpotPrice"] <= 0:
                    smart_buy = data.at[0, "SpotPrice"] * (plan.at[0, "SolarSurplus"] - 3)

        return float(round(normal_buy - smart_buy, 2))
    