"""
Chart for showing the hourly average electricity price saving

Date:
    24-09-2023

"""
# pylint: skip-file

import pandas as pd
import plotly.graph_objs as go

from dash import Dash, dcc, html

from controller import Planner


class SavingsChart:
    """ Show electricity price saving for NormalBuy versus SmartBuy """
    def __init__(self, app: Dash, planner: Planner, 
                 normal_buy: float, better_buy: float, smart_buy: float):
        self._id = "savings-chart"
        self._app = app
        self._normal_buy_price = 0
        self._better_buy_price = 0
        self._smart_buy_price = 0
        self._df = self._calculate_buy_prices(planner.data, planner.plan)
        
        self._normal_buy = normal_buy
        self._better_buy = better_buy
        self._smart_buy = smart_buy

    @property
    def id(self) -> str:
        """ Get component ID """
        return self._id

    @property
    def normal_buy_price(self) -> float:
        """ Get NormalBuyPrice """
        return self._normal_buy_price
    
    @property
    def better_buy_price(self) -> float:
        """ Get BetterBuyPrice """
        return self._better_buy_price
    
    @property
    def smart_buy_price(self) -> float:
        """ Get SmartBuyPrice """
        return self._smart_buy_price

    def render(self) -> html.Div:
        """ Renders the SavingsChart """
        text_str = f"<b>Avg NormalBuyPrice</b>: {self._normal_buy_price} (kr/kWh) | <b>Avg BetterBuyPrice</b>: {self._better_buy_price} (kr/kWh)  | <b>Avg SmartBuyPrice</b>: {self._smart_buy_price} (kr/kWh)"
        text_font = {
            'size': 25,
        }
        fig = go.Figure()

        # NormalBuyPrice
        fig.add_trace(
            go.Bar(
                x=self._df['Time'],
                y=self._df['NormalBuyPrice'],
                name="NormalBuyPrice",
                marker={'color': "#EF553B"}
            )
        )
        
        # BetterBuyPrice
        fig.add_trace(
            go.Bar(
                x=self._df['Time'],
                y=self._df['BetterBuyPrice'],
                name="BetterBuyPrice",
                marker={'color': "#00CC96"}
            )
        )

        # SmartBuyPrice
        fig.add_trace(
            go.Bar(
                x=self._df['Time'],
                y=self._df['SmartBuyPrice'],
                name="SmartBuyPrice",
                marker={'color': "#636EFA"}
            )
        )

        fig.update_layout(title={'text': text_str, 'font': text_font, 
                                 'y': 0.85, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                          xaxis_tickformat="%H",
                          xaxis={'title': 'Hour (GMT+1)', 'tickmode': 'array', 'tickvals': self._df['Time']},
                          yaxis={'title': 'Electricity Costs'},
                          legend={'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.002})
        
        return html.Div(dcc.Graph(figure=fig), id=self._id)

    def _calculate_buy_prices(self, data: pd.DataFrame, plan: pd.DataFrame) -> pd.DataFrame:
        """ Calculates average buy prices for NormalBuy, BetterBuy and SmartBuy

        Args:
            data: Input DataFrame to Planner
            plan: Output DataFrame from Planner

        Returns:
            DataFrame with time and NormalBuyPrice, BetterBuyPrice and SmartBuyPrice
            
        """
        columns = ["Time", "NormalBuyPrice", "BetterBuyPrice", "SmartBuyPrice"]
        df = pd.DataFrame(columns=columns)
        plan_length = plan.index.values.size

        for row in range(0, plan_length):
            action = plan.at[row, "Action"]
            normal_buy_price = data.at[row, "Price"]

            if plan.at[row, "SolarSurplus"] > 0:
                if data.at[row, "SpotPrice"] < 0:
                    better_buy_price = 0
                else:
                    better_buy_price = -abs(data.at[row, "SpotPrice"]) 
            else:
                better_buy_price = data.at[row, "Price"]

            if action == "idle":

                if plan.at[row, "SolarSurplus"] > 0:
                    smart_buy_price = -abs(data.at[row, "SpotPrice"])
                elif plan.at[row, "SolarSurplus"] < 0:
                    smart_buy_price = data.at[row, "Price"]
                else:
                    smart_buy_price = 0

            elif action == "charge":

                if plan.at[row, "SolarSurplus"] > 0:
                    smart_buy_price = data.at[row, "Price"]
                elif plan.at[row, "SolarSurplus"] >= 0 and plan.at[row, "SolarSurplus"] < 3:
                    smart_buy_price = data.at[row, "Price"]
                elif plan.at[row, "SolarSurplus"] > 3:
                    smart_buy_price = -abs(data.at[row, "SpotPrice"])

            else:
                smart_buy_price = 0

            new_row = pd.Series([plan.at[row, "Time"], normal_buy_price, better_buy_price, smart_buy_price], index=columns)
            df = pd.concat([df, new_row.to_frame().T], ignore_index=True)

        self._normal_buy_price = round(df['NormalBuyPrice'].mean(), 2)
        self._better_buy_price = round(df['BetterBuyPrice'].mean(), 2)
        self._smart_buy_price = round(df['SmartBuyPrice'].mean(), 2)
        return df
 