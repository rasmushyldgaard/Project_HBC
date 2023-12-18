"""
GUI Home Tab with quick information

Date:
    16-10-2023

"""

import pandas as pd
import tkinter as tk
from tkinter import ttk
from datetime import datetime

import ui.helperfunctions as hf
from data import Battery
from ui.post_processing import Profit


STATE_OF_CHARGE = 0.87
    
class HomeTab(ttk.Frame):
    """ Class for the Home Tab """
    def __init__(self, parent: ttk.Notebook, scheduler):
        super().__init__(parent)

        # CREATE VARIABLES
        self._current_action = tk.StringVar()
    
        # CREATE SEPARATORS
        self._vertical_separator = ttk.Separator(self, orient='vertical')
        self._horizontal_separator_1 = ttk.Separator(self, orient='horizontal')
        self._horizontal_separator_2 = ttk.Separator(self, orient='horizontal')

        # CREATE LABELS
        self._action_label = ttk.Label(self, text="", font=('Calibri', 60, 'bold'))
        self._reason_label = ttk.Label(self, text="", font=('Calibri', 16, 'italic'))
        self._current_profit_label = ttk.Label(self, text="Current Profit", font=('Calibri', 16, 'bold'))
        self._expected_profit_label = ttk.Label(self, text="Expected Profit", font=('Calibri', 16, 'bold'))
        self._total_profit_label = ttk.Label(self, text="Total Profit", font=('Calibri', 16, 'bold'))
        self._soc_label = ttk.Label(self, text="State Of Charge", font=('Calibri', 16, 'bold'))
        self._energy_loss_label = ttk.Label(self, text="Energy Loss", font=('Calibri', 16, 'bold'))
        self._expected_consumption_label = ttk.Label(self, text="Expected Consumption", font=('Calibri', 16, 'bold'))
        self._current_consumption_label = ttk.Label(self, text="Current Consumption", font=('Calibri', 16, 'bold'))
        self._current_elprice_label = ttk.Label(self, text="Current ElPrice", font=('Calibri', 16, 'bold'))
        self._current_spotprice_label = ttk.Label(self, text="Current SpotPrice", font=('Calibri', 16, 'bold'))
        self._current_solpower_label = ttk.Label(self, text="Current SolPower", font=('Calibri', 16, 'bold'))
        self._time_label = ttk.Label(self, text="Time", font=('Calibri', 16, 'bold'))
        self._next_action_label = ttk.Label(self, text="Next Action At", font=('Calibri', 16, 'bold'))

        # CREATE TEXT
        self._current_profit_text = tk.Text(self, state='disabled',
                                            height=1, width=13, font=('Calibri', 18, 'bold'))
        self._expected_profit_text = tk.Text(self, state='disabled', 
                                                   height=1, width=13, font=('Calibri', 18, 'bold'))
        self._total_profit_text = tk.Text(self, state='disabled', 
                                          height=1, width=13, font=('Calibri', 18, 'bold'))
        self._soc_text = tk.Text(self, state='disabled',
                                 height=1, width=13, font=('Calibri', 18, 'bold'))
        self._energy_loss_text = tk.Text(self, state='disabled',
                                          height=1, width=13, font=('Calibri', 18, 'bold'))
        self._expected_consumption_text = tk.Text(self, state='disabled', 
                                                  height=1, width=13, font=('Calibri', 18, 'bold'))
        self._current_consumption_text = tk.Text(self, state='disabled', 
                                                 height=1, width=13, font=('Calibri', 18, 'bold'))
        self._current_elprice_text = tk.Text(self, state='disabled', 
                                             height=1, width=13, font=('Calibri', 18, 'bold'))
        self._current_spotprice_text = tk.Text(self, state='disabled',
                                               height=1, width=13, font=('Calibri', 18, 'bold'))
        self._current_solpower_text = tk.Text(self, state='disabled', 
                                              height=1, width=13, font=('Calibri', 18, 'bold'))
        self._time_text = tk.Text(self, state='disabled', 
                                  height=1, width=13, font=('Calibri', 18, 'bold'))
        self._next_action_text = tk.Text(self, state='disabled', 
                                         height=1, width=13, font=('Calibri', 18, 'bold'))

        # PLACE COMPONENTS
        self._place_separators()
        self._place_action_section()
        self._place_profit_section()
        self._place_soc_section()
        self._place_consumption_section()
        self._place_data_section()
        self._place_trigger_section()

        # RUN UPDATES ON INIT
        self.update_action_section(scheduler.plan['Action'].iloc[0], scheduler.plan['ActionReason'].iloc[0])
        self.update_profit_section(scheduler.data, scheduler.plan)
        self.update_battery_section(scheduler.battery)
        self.update_consumption_section(scheduler.data)
        self.update_data_section(scheduler.data)
        self.update_time(scheduler)
        self.update_next_action(scheduler.plan)


    def update_action_section(self, action: str, action_reason: str) -> None:
        """ Update the Action and ActionReason labels """
        self._set_action_label(action)
        self._reason_label['text'] = action_reason


    def update_profit_section(self, data: pd.DataFrame, plan: pd.DataFrame) -> None:
        """ Update the profit section """
        profit = Profit(data, plan) # TODO: Temporary
        hf.write_text(self._current_profit_text, "0.0 kr")
        hf.write_text(self._expected_profit_text, f"{profit.expected_profit} kr")
        hf.write_text(self._total_profit_text, "0.0 kr")
        

    def update_battery_section(self, battery: Battery) -> None:
        """ Update the battery section """
        hf.write_text(self._soc_text, f"{round(battery.soc*100, 1)} %")


    def update_consumption_section(self, data: pd.DataFrame) -> None:
        """ Update the consumption section """
        hf.write_text(self._expected_consumption_text, f"{data.at[0, 'ExpectedConsumption']} kWh")
        hf.write_text(self._current_consumption_text, "0 kWh")


    def update_data_section(self, data: pd.DataFrame) -> None:
        """ Update the data section """
        hf.write_text(self._current_elprice_text, f"{data.at[0, 'Price']} kr/kWh")
        hf.write_text(self._current_spotprice_text, f"{data.at[0, 'SpotPrice']} kr/kWh")
        hf.write_text(self._current_solpower_text, f"{round(data.at[0, 'Power'], 4)} kWh")


    def update_time(self, scheduler) -> None:
        """ Updates time_text with current time """
        current_time = datetime.now()
        hf.write_text(self._time_text, current_time.strftime("%H:%M"))
        scheduler.clock_it(current_time)
        self.after(10000, self.update_time, scheduler)


    def update_next_action(self, plan: pd.DataFrame) -> None:
        """ Updates next_action_text with time for next planned action """
        hf.write_text(self._next_action_text, plan.at[1, 'Time'].strftime("%H:%M"))


    def _place_separators(self) -> None:
        """ Place Separator components """
        self._vertical_separator.grid(row=0, column=2, rowspan=9, sticky=f'{tk.N}{tk.S}', padx=20)
        self._horizontal_separator_1.grid(row=2, column=0, columnspan=5, sticky=f'{tk.W}{tk.E}', pady=10)
        self._horizontal_separator_2.grid(row=6, column=0, columnspan=5, sticky=f'{tk.W}{tk.E}', pady=10)


    def _place_action_section(self) -> None:
        """ Place UI components related to current Action and ActionReason """
        # ROW 0, COLUMN 0 & 1
        self._action_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=10)

        # ROW 1, COLUMN 0 & 1
        self._reason_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10)


    def _place_profit_section(self) -> None:
        """ Place UI components related to current, expected and total SmartBuy profits """
        # ROW 3, COLUMN 0 & 1
        self._current_profit_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        self._current_profit_text.grid(row=3, column=1, sticky=tk.W, pady=10)

        # ROW 4, COLUMN 0 & 1
        self._expected_profit_label.grid(row=4, column=0, sticky=tk.W, padx=10)
        self._expected_profit_text.grid(row=4, column=1, sticky=tk.W, pady=10)

        # ROW 5, COLUMN 0 & 1
        self._total_profit_label.grid(row=5, column=0, sticky=tk.W, padx=10)
        self._total_profit_text.grid(row=5, column=1, sticky=tk.W, pady=10)


    def _place_soc_section(self) -> None:
        """ Place UI components related to current SoC of battery """
        # ROW 7, COLUMN 0 & 1
        self._soc_label.grid(row=7, column=0, sticky=tk.W, padx=10, pady=10)
        self._soc_text.grid(row=7, column=1, sticky=tk.W, pady=10)

        # ROW 8, COLUMN 0 & 1
        self._energy_loss_label.grid(row=8, column=0, sticky=tk.W, padx=10, pady=10)
        self._energy_loss_text.grid(row=8, column=1, sticky=tk.W, pady=10)


    def _place_consumption_section(self) -> None:
        """ Place UI components related to expected and current Electricity Consumption """
        # ROW 0, COLUMN 3 & 4
        self._expected_consumption_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        self._expected_consumption_text.grid(row=0, column=4, sticky=tk.W, padx=10)

        # ROW 1, COLUMN 3 & 4
        self._current_consumption_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        self._current_consumption_text.grid(row=1, column=4, sticky=tk.W, padx=10)


    def _place_data_section(self) -> None:
        """ Place UI components related to current ElPrice, SpotPrice and SolPower """
        # ROW 3, COLUMN 3 & 4
        self._current_elprice_label.grid(row=3, column=3, sticky=tk.W, padx=5)
        self._current_elprice_text.grid(row=3, column=4, sticky=tk.W, padx=10)

        # ROW 4, COLUMN 3 & 4
        self._current_spotprice_label.grid(row=4, column=3, sticky=tk.W, padx=5)
        self._current_spotprice_text.grid(row=4, column=4, sticky=tk.W, padx=10)

        # ROW 5, COLUMN 3 & 4
        self._current_solpower_label.grid(row=5, column=3, sticky=tk.W, padx=5)
        self._current_solpower_text.grid(row=5, column=4, sticky=tk.W, padx=10)


    def _place_trigger_section(self) -> None:
        """ Place UI components related to current time and next expected trigger for algorithm """
        # ROW 7, COLUMN 3 & 4
        self._time_label.grid(row=7, column=3, sticky=tk.W, padx=5, pady=10)
        self._time_text.grid(row=7, column=4, sticky=tk.W, padx=10, pady=10)

        # ROW 8, COLUMN 3 & 4
        self._next_action_label.grid(row=8, column=3, sticky=tk.W, padx=5, pady=10)
        self._next_action_text.grid(row=8, column=4, sticky=tk.W, padx=10, pady=10)
        

    def _set_action_label(self, action: str) -> None:
        """ Set label for current action

        Args:
            action: String of current action
                    'idle', 'charge' or 'equalize'

        """
        self._action_label['text'] = action.upper()

        if action == 'IDLE':
            self._action_label['foreground'] = 'blue'
        elif action == 'CHARGE':
            self._action_label['foreground'] = 'red'
        else:
            self._action_label['foreground'] = 'green'
