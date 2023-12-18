"""
Subplots to display electricity prices and expected consumption

Date:
    22-09-2023

"""
# pylint: skip-file

import plotly.graph_objs as go

from dash import Dash, dcc, html
from plotly.subplots import make_subplots

from controller import Planner


class DataPlots:
    """ Subplots of electricity and expected consumption """
    def __init__(self, app: Dash, planner: Planner):
        self._app = app
        self._df_electricity = planner.data.loc[:, ['Time', 'Price']]
        self._df_consumption = planner.data.loc[:, ['Time', 'ExpectedConsumption']]
        self._df_solar = planner.data.loc[:, ['Time', 'Power']]
        self._df_battery = planner.plan.loc[:, ['Time', 'BatteryExpected']]

    def render_first_row(self) -> html.Div:
        """ Renders the subplots for electricity and expected consumption """
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Electricity Prices (kr/kWh)", 
                                                            "Household Electricity Consumption Expectancy (kWh)"))

        fig.add_trace(
            go.Bar(
                x=self._df_electricity['Time'],
                y=self._df_electricity['Price'],
                name='EL',
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Bar(
                x=self._df_consumption['Time'],
                y=self._df_consumption['ExpectedConsumption'],
                name='EC',
            ),
            row=1,
            col=2
        )

        fig.update_xaxes(title_text="Hour (GMT+1)", row=1, col=1)
        fig.update_xaxes(title_text="Hour (GMT+1)", row=1, col=2)
        fig.update_yaxes(title_text="Prices", row=1, col=1)
        fig.update_yaxes(title_text="Consumption", row=1, col=2)
        

        fig.update_layout(xaxis_tickformat="%H", xaxis2_tickformat="%H",
                          xaxis={'tickmode': 'array', 'tickvals': self._df_electricity['Time']},
                          xaxis2={'tickmode': 'array', 'tickvals': self._df_consumption['Time']},
                          showlegend=False)

        return html.Div(dcc.Graph(figure=fig), id="data-plots-first-row")
    

    def render_second_row(self) -> html.Div:
        """ Renders the subplots for solar power and battery capacity """
        fig = make_subplots(rows=1, cols=2, subplot_titles=("PV Power Expectancy from Solar Power Plant (kWh)",
                                                            "Battery Capacity Expectancy (kWh)"))

        fig.add_trace(
            go.Bar(
                x=self._df_solar['Time'],
                y=self._df_solar['Power'],
                name='SL',
                marker={'color': "#FECB52"}
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Bar(
                x=self._df_battery['Time'],
                y=self._df_battery['BatteryExpected'],
                name='BT',
                marker={'color': "#AB63FA"}
            ),
            row=1,
            col=2
        )

        fig.update_xaxes(title_text="Hour (GMT+1)", row=1, col=1)
        fig.update_xaxes(title_text="Hour (GMT+1)", row=1, col=2)
        fig.update_yaxes(title_text="Power", row=1, col=1)
        fig.update_yaxes(title_text="Battery Capacity", row=1, col=2)

        fig.update_layout(xaxis_tickformat="%H", xaxis2_tickformat="%H",
                          xaxis={'tickmode': 'array', 'tickvals': self._df_solar['Time']},
                          xaxis2={'tickmode': 'array', 'tickvals': self._df_battery['Time']},
                          showlegend=False)
        
        return html.Div(dcc.Graph(figure=fig), id="data-plots-second-row")