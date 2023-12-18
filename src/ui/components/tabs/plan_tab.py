"""
GUI Plan Tab with a full view of the generated plan

Date:
    23-10-2023

"""

from datetime import timedelta
import pandas as pd
import tkinter as tk
from tkinter import ttk

from controller import Planner


class PlanTab(ttk.Frame):
    """ Class for the Plan Tab """
    def __init__(self, parent: ttk.Notebook, planner: Planner):
        super().__init__(parent)
        self._plan_view = ttk.Treeview(self, takefocus=False, selectmode='none')
        self._plan_view['columns'] = ("Action", "Start", "End", "Reason")
        self._plan_view.column("#0", width=0, stretch=False)
        self._plan_view.column("Action", anchor=tk.W, width=40)
        self._plan_view.column("Start", anchor=tk.W, width=40)
        self._plan_view.column("End", anchor=tk.W, width=40)
        self._plan_view.column("Reason", anchor=tk.W, width=120)
        self._plan_view.heading("Action", text="Action", anchor=tk.W)
        self._plan_view.heading("Start", text="Start", anchor=tk.W)
        self._plan_view.heading("End", text="End", anchor=tk.W)
        self._plan_view.heading("Reason", text="Reason", anchor=tk.W)
        self._fill_plan_view(planner.plan)

        self._plan_view.bind('<Motion>', 'break')
        self._plan_view.pack(expand=True, fill='both')


    def update_plan(self, plan: pd.DataFrame) -> None:
        """ Update the PlanTab view

        Args:
            plan: Generated plan from Controller

        """
        self._fill_plan_view(plan)


    def _fill_plan_view(self, plan: pd.DataFrame) -> None:
        """ Fills the Plan treeview with actions, timestamps and reasons

        Args:
            plan: Generated plan from Controller

        """
        plan_length = plan.index.values.size

        for row in range(0, plan_length):
            start_time = plan.at[row, 'Time']
            end_time = plan.at[row, 'Time'] + timedelta(hours=1)
            
            action = (f'{plan.at[row, "Action"]}',
                      f'{start_time}',
                      f'{end_time}',
                      f'{plan.at[row, "ActionReason"]}')
            self._plan_view.insert('', tk.END, values=action)
