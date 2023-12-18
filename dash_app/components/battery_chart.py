"""
Chart for showing battery charging and discharging

Date:
    02-10-2023

"""
# pylint: skip-file

import pandas as pd
import plotly.graph_objs as go

from dash import Dash, dcc, html

from controller import Planner


class BatteryChart:
    """ Chart for showing when battery is charging/discharging versus total capacity """
    def __init__(self, app: Dash, planner: Planner):
        self._id = "battery-chart"
        self._app = app
        self._total_battery_loss = 0
        self._hourly_avg_battery_loss = 0
        self._calculate_battery_loss(planner.plan)
        self._df = planner.plan.loc[:, ["Time", "Action", "BatteryDelta", "BatteryExpected"]]

    @property
    def id(self) -> str:
        """ Get component ID """
        return self._id
    
    @property
    def total_battery_loss(self) -> float:
        """ Get total energy loss for battery """
        return self._total_battery_loss
    
    @property
    def hourly_avg_battery_loss(self) -> float:
        """ Get hourly average energy loss for battery """
        return self._hourly_avg_battery_loss

    def render(self) -> html.Div:
        """ Renders the chart for BatteryDelta vs. BatteryExpected """
        text_str = f"<b>Hourly Average Battery Loss</b>: {self._hourly_avg_battery_loss} (kWh) | <b>Total Battery Loss</b>: {self._total_battery_loss} (kWh)"
        text_font = {
            'size': 25,
        }
        fig = go.Figure()

        # BatteryDelta
        fig.add_trace(
            go.Bar(
                x=self._df["Time"],
                y=self._df["BatteryDelta"],
                name="BatteryDelta",
                marker={'color': "#FF97FF"}
            )
        )

        # BatteryExpected
        fig.add_trace(
            go.Bar(
                x=self._df["Time"],
                y=self._df["BatteryExpected"],
                name="BatteryExpected",
                marker={'color': "#AB63FA"}
            )
        )

        # Actions
        fig.add_trace(
            go.Scatter(
                x=self._df["Time"],
                y=self._df["Action"],
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
                          yaxis={'title': 'Amplitude'},
                          yaxis2={'anchor': 'y', 'overlaying': 'y', 'side': 'right', 'categoryorder': 'array',
                                  'categoryarray': ['charge', 'idle', 'equalize'], 'title': 'Actions'},
                          legend={'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.002})
        fig.data[2].update(yaxis='y2')

        return html.Div(dcc.Graph(figure=fig), id=self.id)
    
    def _calculate_battery_loss(self, plan: pd.DataFrame) -> None:
        """ Calculate hourly average battery loss and total battery loss

        Args:
            plan: Output DataFrame from Planner
            
        """
        columns = ["Time", "BatteryLoss"]
        df = pd.DataFrame(columns=columns)
        battery_loss = 0
        plan_length = plan.index.values.size

        for row in range(0, plan_length):
            battery_delta = abs(plan.at[row, "BatteryDelta"])
            battery_loss = battery_delta * 0.1

            new_row = pd.Series([plan.at[row, "Time"], battery_loss], index=columns)
            df = pd.concat([df, new_row.to_frame().T], ignore_index=True)

        self._hourly_avg_battery_loss = round(df['BatteryLoss'].mean(), 2)
        self._total_battery_loss = round(df['BatteryLoss'].sum(), 2)

