"""
Layout of HomeBatteryController Dash app

Date:
    20-08-2023

"""
# pylint: skip-file

from datetime import datetime
from dash import Dash, html

from .chart_dropdown import ChartDropDown
from .actions_chart import ActionsChart
from .data_plots import DataPlots
from .savings_chart import SavingsChart
from .accumulated_savings import AccumulatedSavingsChart
from .battery_chart import BatteryChart

from controller import Planner

class Layout:
    """ Layout of Dash app """
    def __init__(self, app: Dash, planner: Planner):
        self.app = app
        self.planner = planner
        self.title = app.title
        self.view = html.Div(id="view-container")
        self.accumulated_savings = AccumulatedSavingsChart(app, planner)
        self.actions_chart = ActionsChart(app, planner, 
                                          self.accumulated_savings.normal_buy, 
                                          self.accumulated_savings.better_buy,
                                          self.accumulated_savings.smart_buy)
        self.savings_chart = SavingsChart(app, planner, 
                                          self.accumulated_savings.normal_buy,
                                          self.accumulated_savings.better_buy, 
                                          self.accumulated_savings.smart_buy)
        self.battery_chart = BatteryChart(app, planner)
        self.data_plots = DataPlots(app, planner)
        self.chart_dropdown = ChartDropDown(app, 
                                            self.actions_chart, 
                                            self.savings_chart,
                                            self.accumulated_savings,
                                            self.battery_chart)

    def create(self) -> html.Div:
        """ Create the HTML Layout """
        return html.Div(
            className="app-div",
            children=[
                html.H1(self.title, style={'textAlign': 'center'}),
                html.Hr(),
                html.Div(
                    className="dropdown-container",
                    children=[
                        self.chart_dropdown.render()
                    ]
                ),
                self.current_day_title(self.planner),
                self.view,
                self.data_plots.render_first_row(),
                self.data_plots.render_second_row()
            ]
        )
    
    def current_day_title(self, planner: Planner) -> html.H2:
        """ Title for showing days and dates

        Args:
            Planner object

        Returns:
            HTML Header2
            
        """
        first_date = planner.time_window[0].date().strftime("%d-%m-%Y")
        second_date = planner.time_window[1].date().strftime("%d-%m-%Y")

        if first_date == second_date:
            title = f"{planner.time_window[0].strftime('%A')} ({first_date})"
        else:
            title = f"{planner.time_window[0].strftime('%A')} ({first_date}) / {planner.time_window[1].strftime('%A')} ({second_date})"

        return html.H2(title, style={'textAlign': 'center'})