"""
GUI Layout of Application Tabs

Date:
    17-10-2023

"""

import tkinter as tk
from tkinter import ttk

from ui.components import HomeTab, PlanTab, GraphsTab, ProfileTab

WIDTH = 800
HEIGHT = 480

class TabLayout(ttk.Notebook):
    """ Application Tabs """
    def __init__(self, parent: tk.Tk, settings: dict[str, str], scheduler):
        super().__init__(parent, height=HEIGHT, width=WIDTH)
        self.home_tab = HomeTab(self, scheduler)
        self.plan_tab = PlanTab(self, scheduler)
        self.graphs_tab = GraphsTab(self, scheduler)
        self.profile_tab = ProfileTab(self, settings, scheduler)
        self.logging_tab = ttk.Frame(self)

        self.add(self.home_tab, text="Home")
        self.add(self.plan_tab, text="Plan")
        self.add(self.graphs_tab, text="Graphs")
        self.add(self.profile_tab, text="Profile")
        
        # TODO: Logging Tab
        self.add(self.logging_tab, text="Logging")
        self.pack(expand=True, fill='both')


        