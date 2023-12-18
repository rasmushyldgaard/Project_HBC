"""
GUI Application for HomeBatteryController

Date:
    16-10-2023

"""


import tkinter as tk
from tkinter import ttk

from .scheduler import Scheduler
from .tab_layout import TabLayout
from database import Database


WIDTH = 800
HEIGHT = 480

class Application(tk.Tk):
    """ Application Root """
    def __init__(self, os: str):
        super().__init__()
        self.title("HomeBatteryController")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self._init_database()
        self._settings = self._get_settings()
        self._scheduler = Scheduler(self, self._settings)
        self._tabs = TabLayout(self, self._settings, self._scheduler)
        self._style()
        self.protocol("WM_DELETE_WINDOW", self._quit)
        if os == 'posix':
            self.overrideredirect(True)

    def update_ui(self, *args, section: str = '') -> None:
        """ Updates entire UI with new information or only specified section
        if no section is given. 

        Args:
            section: The section to update

        """
        if section == 'battery':
            self._tabs.home_tab.update_battery_section(self._scheduler.battery)
        elif section == 'action':
            self._tabs.home_tab.update_action_section(*args)
        else:
            self._tabs.home_tab.update_action_section(*args)
            self._tabs.home_tab.update_profit_section(self._scheduler.data, self._scheduler.plan)
            self._tabs.home_tab.update_battery_section(self._scheduler.battery)
            self._tabs.home_tab.update_consumption_section(self._scheduler.data)
            self._tabs.home_tab.update_data_section(self._scheduler.data)
            self._tabs.home_tab.update_next_action(self._scheduler.plan)
            

    def _init_database(self) -> None:
        """ Initialize Database and create tables if they don't exist """
        db = Database()
        db.create_missing_tables()  # Create tables if missing in database

    def _get_settings(self) -> dict[str, str]:
        """ Get saved user settings from database
            If no saved user settings, create new settings in memory
        
        Returns:
            Dict with user settings or default settings

        """
        db = Database()

        if not db.check_for_empty_table('settings'):
            return db.load_settings()

        return {
            'address': '',
            'city': '',
            'postal': '',
            'country': '',
            'price_area': 'DK1',
            'solar_strategy': 'Sell All',
            'solcast_key': '',
            'solcast_ids': '',
            'tariff_company': 'Radius Elnet A/S',
            'provider': '',
            'basis': '',
            'prices': '',
            'capacity': '20',
            'effectivity': '90',
            'threshold': '0',
            'max_rate': '3',
            'model': 'SmartBuy'
        }
    
    def _style(self) -> None:
        """ Application Style """
        style = ttk.Style()
        current_theme = style.theme_use()
        style.theme_settings(current_theme, settings={"TNotebook.Tab": {"configure": {"padding": [50, 5]}}})

    def _quit(self):
        """ Clean up after shutdown """
        self._scheduler.shutdown()
        self.quit()
        self.destroy()
