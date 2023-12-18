"""
A chart of which MiniCon actions to take the next day!

Date:
    20-08-2023

"""
# pylint: skip-file

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from dash import Dash, dcc, html

from controller import Planner


class ActionsChart:
    """ Chart of MiniCon actions to take every hour relative to Planner input parameters """
    def __init__(self, app: Dash, planner: Planner, 
                 normal_buy: float, better_buy: float, smart_buy: float):
        self._id = "action-chart"
        self._app = app
        self._actions = planner.plan.loc[:, ["Time", "Action"]]
        self._df = self._get_dataframe(planner.data, planner.plan)
        self._normal_buy = normal_buy
        self._better_buy = better_buy
        self._smart_buy = smart_buy
    
    @property
    def id(self) -> str:
        """ Get component ID """
        return self._id

    def render(self) -> html.Div:
        """ Renders the ActionChart """

        # Use the figure title to show NormalBuy and SmartBuy costs
        text_str = f"<b>NormalBuy</b>: {self._normal_buy} (kr) | <b>BetterBuy</b>: {self._better_buy} (kr) | <b>SmartBuy</b>: {self._smart_buy} (kr)"
        text_font = {
            'size': 25,
        }

        fig = px.bar(self._df, x='Time', y='Amplitude', color=self._df.index,
                     color_discrete_sequence=["#636EFA", "#EF553B", "#FECB52", "#AB63FA"],
                     barmode='group', labels={'Time': 'Hour (GMT+1)'})
        fig.update_traces(textposition="outside")
        
        # Second plot within ActionChart is the charge plan with actions
        fig.add_trace(
            go.Scatter(
                x=self._actions['Time'],
                y=self._actions['Action'],
                name="",
                line={'color': 'rgba(0, 0, 0, 0.4)'},
                mode='lines+markers',
                showlegend=False
            ),
        )

        fig.update_layout(title={'text': text_str, 'font': text_font, 
                                 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                          xaxis_tickformat="%H",
                          xaxis={'tickmode': 'array', 'tickvals': self._df['Time']},
                          yaxis2={'anchor': 'y', 'overlaying': 'y', 'side': 'right', 'categoryorder': 'array',
                                  'categoryarray': ['charge', 'idle', 'equalize'], 'title': 'Actions'},
                          legend={'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.002, 'title_text': ''})
        fig.data[4].update(yaxis='y2')

        return html.Div(dcc.Graph(figure=fig), id=self.id)
    
    def _get_dataframe(self, data: pd.DataFrame, plan: pd.DataFrame) -> pd.DataFrame:
        """ Get the DataFrame for ActionChart to plot

        Args:
            data: Input DataFrame to Planner

        Returns:
            DataFrame with electricity and expected consumption y-axes normalized

        """
        df_electricity = data.loc[:, ['Time', 'Price']]
        df_electricity = df_electricity.rename(columns={'Price': 'Amplitude'})
        df_electricity['Amplitude'] = round((df_electricity['Amplitude'] / df_electricity['Amplitude'].max()), 2)
        df_electricity['Type'] = 'ElPrice'
        
        df_consumption = data.loc[:, ['Time', 'ExpectedConsumption']]
        df_consumption = df_consumption.rename(columns={'ExpectedConsumption': 'Amplitude'})
        df_consumption['Amplitude'] = round((df_consumption['Amplitude'] / df_consumption['Amplitude'].max()), 2)
        df_consumption['Type'] = 'Consumption'

        df_solar = data.loc[:, ['Time', 'Power']]
        df_solar = df_solar.rename(columns={'Power': 'Amplitude'})
        df_solar['Amplitude'] = round((df_solar['Amplitude'] / df_solar['Amplitude'].max()), 2)
        df_solar['Type'] = 'SolPower'

        df_battery = plan.loc[:, ['Time', 'BatteryExpected']]
        df_battery = df_battery.rename(columns={'BatteryExpected': 'Amplitude'})
        df_battery['Amplitude'] = round((df_battery['Amplitude'] / df_battery['Amplitude'].max()), 2)
        df_battery['Type'] = 'BatteryCap'
        
        df = pd.concat([df_electricity, df_consumption])
        df = pd.concat([df, df_solar])
        df = pd.concat([df, df_battery])
        df = df.sort_values('Time', ignore_index=False)
        df = df.set_index('Type')
        
        # Always have the labels in a fixed order, so the bar charts doesn't randmly mismatch.
        desired_order = ['ElPrice', 'Consumption', 'SolPower', 'BatteryCap']
        custom_index = [label for label in desired_order if label in df.index]
        df = df.loc[custom_index]

        return df
    