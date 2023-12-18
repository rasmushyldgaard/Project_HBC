"""
Dropdown menu for switching between charts

Date:
    25-09-2023

"""
# pylint: skip-file

from dash import Dash, html, dcc, Input, Output

from .actions_chart import ActionsChart
from .savings_chart import SavingsChart
from .accumulated_savings import AccumulatedSavingsChart
from .battery_chart import BatteryChart

class ChartDropDown:
    """ Dropdown menu for switching between charts """
    def __init__(self, app: Dash, 
                 actions_chart: ActionsChart, 
                 savings_chart: SavingsChart, 
                 accumulated_savings_chart: AccumulatedSavingsChart,
                 battery_chart: BatteryChart):
        self._id = "chart-dropdown"
        self._app = app
        self._charts = ["Actions", "Battery", "Savings", "AccumulatedSavings"]
        self._actions_chart = actions_chart
        self._savings_chart = savings_chart
        self._accumulated_savings = accumulated_savings_chart
        self._battery_chart = battery_chart

    @property
    def id(self) -> str:
        """ Get component ID """
        return self._id
        
    def render(self) -> html.Div:
        """ Renders the dropdown menu for charts """

        @self._app.callback(
            Output('view-container', 'children'),
            Input(self.id, 'value')
        )
        def change_view(value):
            """ Callback for changing which chart to render based on dropdown value """
            if value == "Actions":
                return self._actions_chart.render()
            elif value == "Savings":
                return self._savings_chart.render()
            elif value == "AccumulatedSavings":
                return self._accumulated_savings.render()
            elif value == "Battery":
                return self._battery_chart.render()
            else:
                # Default view
                return self._actions_chart.render()

        return html.Div(
            children=[
                html.H6("Change view", style={'padding-left': '1.1%'}),
                dcc.Dropdown(
                    id=self.id,
                    options=self._charts,
                    value=self._charts[0],
                    clearable=False,
                    searchable=False,
                    style={'width': 200, 'padding-left': '1%'}
                )
            ]
        )