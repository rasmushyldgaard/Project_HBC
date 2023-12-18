"""
Chart of accumulated NormalBuy and SmartBuy electricity costs

Date:
    25-09-2023
    
"""
# pylint: skip-file

import pandas as pd
import plotly.graph_objs as go

from dash import Dash, dcc, html

from controller import Planner


class AccumulatedSavingsChart:
    """ Chart of the accumulated NormalBuy and SmartBuy electricity costs """
    def __init__(self, app: Dash, planner: Planner):
        self._id = "accumulated-savings"
        self._app = app
        self._normal_buy = 0
        self._better_buy = 0
        self._smart_buy = 0        
        self._df = self._get_dataframe(planner.data, planner.plan)
        self._actions = planner.plan.loc[:, ["Time", "Action"]]

    @property
    def id(self) -> str:
        """ Get component ID """
        return self._id

    @property
    def normal_buy(self) -> float:
        """ Get NormalBuy cost """
        return self._normal_buy
    
    @property
    def better_buy(self) -> float:
        """ Get BetterBuy cost """
        return self._better_buy

    @property
    def smart_buy(self) -> float:
        """ Get SmartBuy cost """
        return self._smart_buy

    def render(self) -> html.Div:
        """ Renders the AccumulatedSavingsChart """
        text_str = f"<b>NormalBuy</b>: {self._normal_buy} (kr) | <b>BetterBuy</b>: {self._better_buy} (kr) | <b>SmartBuy</b>: {self._smart_buy} (kr)"
        text_font = {
            'size': 25,
        }
        fig = go.Figure()

        # NormalBuy
        fig.add_trace(
            go.Scatter(
                x=self._df['Time'],
                y=self._df['NormalBuy'],
                name="NormalBuy",
                marker={'color': "#EF553B"}
            )
        )

        # BetterBuy
        fig.add_trace(
            go.Scatter(
                x=self._df['Time'],
                y=self._df['BetterBuy'],
                name="BetterBuy",
                marker={'color': "#00CC96"}
            )
        )
        
        # SmartBuy
        fig.add_trace(
            go.Scatter(
                x=self._df['Time'],
                y=self._df['SmartBuy'],
                name="SmartBuy",
                marker={'color': "#636EFA"}
            )
        )

        # Actions
        fig.add_trace(
            go.Scatter(
                x=self._actions["Time"],
                y=self._actions["Action"],
                name="",
                line={'color': 'rgba(0, 0, 0, 0.4)'},
                mode='lines+markers',
                showlegend=False
            ),
        )

        fig.update_layout(title={'text': text_str, 'font': text_font, 
                                 'y': 0.85, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                          xaxis_tickformat="%H",
                          xaxis={'title': 'Hour (GMT+1)', 'tickmode': 'array', 'tickvals': self._df['Time']},
                          yaxis={'title': 'Electricity Costs'},
                          yaxis2={'anchor': 'y', 'overlaying': 'y', 'side': 'right', 'categoryorder': 'array',
                                  'categoryarray': ['charge', 'idle', 'equalize'], 'title': 'Actions'},
                          legend={'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.002})
        fig.data[3].update(yaxis='y2')
        
        return html.Div(dcc.Graph(figure=fig), id=self.id)

    def _get_dataframe(self, data: pd.DataFrame, plan: pd.DataFrame) -> pd.DataFrame:
        """ Get the DataFrame for AccumulatedSavingsChart to plot

        Args:
            data: Input DataFrame to Planner
            plan: Output DataFrame from Planner

        Returns:
            DataFrame with time and accumulated NormalBuy, BetterBuy and SmartBuy costs

        """
        columns = ["Time", "NormalBuy", "BetterBuy", "SmartBuy"]
        df = pd.DataFrame(columns=columns)
        normal_buy = 0
        better_buy = 0
        smart_buy = 0
        plan_length = plan.index.values.size
        
        for row in range(0, plan_length):
            action = plan.at[row, "Action"]
            normal_buy += data.at[row, "ExpectedConsumption"] * data.at[row, "Price"]

            if plan.at[row, "SolarSurplus"] > 0:
                if not data.at[row, "SpotPrice"] <= 0:
                    better_buy -= data.at[row, "SpotPrice"] * plan.at[row, "SolarSurplus"] 
            else:
                better_buy += data.at[row, "Price"] * abs(plan.at[row, "SolarSurplus"]) 

            if action == "idle":
                
                if plan.at[row, "SolarSurplus"] > 0:
                    if not data.at[row, "SpotPrice"] <= 0:
                        smart_buy -= data.at[row, "SpotPrice"] * plan.at[row, "SolarSurplus"]   
                elif plan.at[row, "SolarSurplus"] < 0:
                    smart_buy += data.at[row, "Price"] * abs(plan.at[row, "SolarSurplus"])

            elif action == "charge":
                
                if plan.at[row, "SolarSurplus"] < 0:
                    smart_buy += data.at[row, "Price"] * abs(plan.at[row, "SolarSurplus"])
                    smart_buy += data.at[row, "Price"] * plan.at[row, "ElNetCharge"]
                elif plan.at[row, "SolarSurplus"] >= 0 and plan.at[row, "SolarSurplus"] < 3:
                    smart_buy += data.at[row, "Price"] * plan.at[row, "ElNetCharge"]
                elif plan.at[row, "SolarSurplus"] > 3:
                    if not data.at[row, "SpotPrice"] <= 0:
                        smart_buy -= data.at[row, "SpotPrice"] * (plan.at[row, "SolarSurplus"] - 3)

            else:
                pass

            new_row = pd.Series([plan.at[row, "Time"], normal_buy, better_buy, smart_buy], index=columns)
            df = pd.concat([df, new_row.to_frame().T], ignore_index=True)

        self._normal_buy = round(normal_buy, 2)
        self._better_buy = round(better_buy, 2)
        self._smart_buy = round(smart_buy, 2)
        return df
