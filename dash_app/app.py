"""
Dash app for HomeBatteryController

Date:
    20-08-2023

Description:
    Run application with `python app.py`
    Access app in browser on localhost at 127.0.0.1:8050

"""
# pylint: skip-file

from dash import Dash
from dash_bootstrap_components.themes import BOOTSTRAP

from components import Layout

from controller import Planner


app = Dash(external_stylesheets=[BOOTSTRAP])
app.title = "HomeBatteryController"
app.layout = Layout(app, Planner()).create()


if __name__ == "__main__":
    app.run(debug=True)