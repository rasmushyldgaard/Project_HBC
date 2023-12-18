"""
GUI Graphs Tab for plotting data graphs

Date:
    25-10-2023

"""

import tkinter as tk
import matplotlib.pyplot as plt

from tkinter import ttk
from matplotlib import ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from controller import Planner


GRAPHS = (
    'ElPrices',
    'Consumption',
    'SolPower',
    'BatteryCap'
)

class GraphsTab(ttk.Frame):
    """ Class for the Graphs Tab """
    def __init__(self, parent: ttk.Notebook, planner: Planner):
        super().__init__(parent)

        # CREATE VARIABLES
        self._data, self._plan = planner.data, planner.plan
        self._current_graph = tk.StringVar(value=GRAPHS[0])
        self._current_graph.trace_add('write', self._plot_graph)
        self._graph_content = {
            GRAPHS[0]: {
                'df': 'data',
                'column': "Price", 
                'title': 'Electricity Prices',
                'ylabel': 'Price (kr/kWh)',
                'ytick': 0.5
            },
            GRAPHS[1]: {
                'df': 'data',
                'column': "ExpectedConsumption",
                'title': 'Household Consumption Expectancy',
                'ylabel': 'Consumption (kWh)',
                'ytick': 0.2
            },
            GRAPHS[2]: {
                'df': 'data',
                'column': "Power",
                'title': 'Expected Production Of Solar Panels',
                'ylabel': 'Power (kWh)',
                'ytick': 0.1
            },
            GRAPHS[3]: {
                'df': 'plan',
                'column': "BatteryExpected",
                'title': 'Battery Capacity Expectancy',
                'ylabel': 'Capacity (kWh)',
                'ytick': 0.5
            }
        }

        # CREATE LABELS
        self._plot_label = ttk.Label(self, text="Plot", font=('Calibri', 20, 'bold'))
        
        # CREATE DROPDOWN
        self._graphs_dropdown = ttk.Combobox(self, state='readonly',
                                             width=17, values=GRAPHS,
                                             textvariable=self._current_graph,
                                             takefocus=False)
        
        # CREATE GRAPH
        self._fig, self._ax = plt.subplots(figsize=(7, 4.5))
        self._graph_canvas = FigureCanvasTkAgg(self._fig, self)
        
        # INIT FUNCTIONS
        self._place_components()
        self._plot_graph()


    def _plot_graph(self, *args) -> None: # pylint: disable=unused-argument
        """ Callback for plotting the correct graph based on current entry value """
        self._ax.clear()

        # Same x-axis used on every graph
        df_time = self._data.loc[:, "Time"]
        x_length = len(df_time)
        x_range = range(x_length)
        time_in_hours = [time.hour for time in df_time]
        self._ax.set_xlabel('Time (hour)')

        if x_length > 24:
            self._ax.set_xticks(x_range, time_in_hours, fontsize='x-small')
            width = 0.5
        else:
            self._ax.set_xticks(x_range, time_in_hours)
            width = 0.8

        current_graph = self._current_graph.get()
        if self._graph_content[current_graph]['df'] == 'plan':
            y = self._plan.loc[:, self._graph_content[current_graph]['column']]  
        else:
            y = self._data.loc[:, self._graph_content[current_graph]['column']]

        self._ax.bar(x_range, y, width=width)
        self._ax.yaxis.set_major_locator(ticker.MultipleLocator(
                                         self._graph_content[current_graph]['ytick'])) # type: ignore
        self._ax.set_title(self._graph_content[current_graph]['title'])
        self._ax.set_ylabel(self._graph_content[current_graph]['ylabel'])
        self._graph_canvas.draw()


    def _place_components(self) -> None:
        """ Place UI components related to Graphs Tab """
        # ROW 0, COLUMN 0
        self._plot_label.grid(row=0, column=0, sticky=f'{tk.W}{tk.N}', padx=5)

        # ROW 1, COLUMN 1
        self._graphs_dropdown.grid(row=0, column=0, sticky=f'{tk.W}{tk.N}', padx=5, pady=40)

        # Canvas to hold graphs
        self._graph_canvas.get_tk_widget().grid(row=0, column=1, rowspan=3, columnspan=3)
