"""
GUI Profile Tab for storing user settings

Date:
    16-10-2023

"""

import tkinter as tk
from tkinter import ttk

from .geolocator import GeoLocator
from .danish_regions import DANISH_REGIONS
from .solar_panels_top import SolarPanelsTop
from .supplement_top import SupplementTop
from database import Database
from data.electricity import TARIFF_COMPANY


class ProfileTab(ttk.Frame):
    """ Class for the Profile Tab """
    def __init__(self, parent: ttk.Notebook, settings: dict[str, str], scheduler):
        super().__init__(parent)

        # CREATE VARIABLES
        self._settings = settings
        self._scheduler = scheduler
        self._address_var = tk.StringVar()
        self._city_var = tk.StringVar()
        self._postal_code_var = tk.StringVar()
        self._country_var = tk.StringVar()
        self._solar_strategy_var = tk.StringVar(value='Sell All')
        self._solcast_key_var = tk.StringVar()
        self._solcast_resource_ids_list = tk.StringVar() # List type stored as comma separated string

        self._grid_company_var = tk.StringVar()
        self._provider_company_var = tk.StringVar()
        self._basis_var = tk.StringVar(value='Flat')
        self._prices_var = tk.StringVar()

        self._battery_capacity_var = tk.StringVar()
        self._battery_effectivity_var = tk.StringVar()
        self._battery_threshold_var = tk.StringVar()
        self._battery_max_charge_rate_var = tk.StringVar()

        self._algorithm_model_var = tk.StringVar(value='SmartBuy')

        # CREATE SEPARATORS
        self._vertical_separator = ttk.Separator(self, orient='vertical')
        self._horizontal_separator_1 = ttk.Separator(self, orient='horizontal')
        self._horizontal_separator_2 = ttk.Separator(self, orient='horizontal')

        # CREATE LABELS
        self._household_label = ttk.Label(self, text="Household", font=('Calibri', 20, 'bold'))
        self._address_label = ttk.Label(self, text="Address", font=('Calibri', 14, 'bold'))
        self._city_label = ttk.Label(self, text="City", font=('Calibri', 14, 'bold'))
        self._postal_code_label = ttk.Label(self, text="Postal Code", font=('Calibri', 14, 'bold'))
        self._country_label = ttk.Label(self, text="Country", font=('Calibri', 14, 'bold'))
        self._extra_label = ttk.Label(self, text="Extra", font=('Calibri', 20, 'bold'))
        self._solar_panels_label = ttk.Label(self, text="Solar Panels", font=('Calibri', 14, 'bold'))
        self._ev_label = ttk.Label(self, text="Electric Vehicle", font=('Calibri', 14, 'bold'))
        self._provider_label = ttk.Label(self, text="Electric Utilities", font=('Calibri', 20, 'bold'))
        self._grid_company_label = ttk.Label(self, text="Grid Company" , font=('Calibri', 14, 'bold'))
        self._provider_company_label = ttk.Label(self, text="Provider Company", font=('Calibri', 14, 'bold'))
        self._provider_supplement_label = ttk.Label(self, text="SpotPrice Supplement", font=('Calibri', 14, 'bold'))
        self._battery_label = ttk.Label(self, text="Battery", font=('Calibri', 20, 'bold'))
        self._battery_capacity_label = ttk.Label(self, text="Capacity (kWh)", font=('Calibri', 14, 'bold'))
        self._battery_effectivity_label = ttk.Label(self, text="Effectivity (%)", font=('Calibri', 14, 'bold'))
        self._battery_threshold_label = ttk.Label(self, text="Threshold (%)", font=('Calibri', 14, 'bold'))
        self._battery_max_charge_rate_label = ttk.Label(self, text="Max Charge Rate (kWh)", 
                                                        font=('Calibri', 14, 'bold'))
        self._algorithm_label = ttk.Label(self, text="Optimization", font=('Calibri', 20, 'bold'))
        self._algorithm_model_label = ttk.Label(self, text="Model", font=('Calibri', 14, 'bold'))
        self._algorithm_vacation_label = ttk.Label(self, text="Planned Vacation", font=('Calibri', 14, 'bold'))
        
        # CREATE ENTRIES
        self._address_entry = ttk.Entry(self, takefocus=False, textvariable=self._address_var)
        self._city_entry = ttk.Entry(self, takefocus=False, textvariable=self._city_var)
        self._postal_code_entry = ttk.Entry(self, takefocus=False, textvariable=self._postal_code_var)
        self._country_entry = ttk.Entry(self, takefocus=False, textvariable=self._country_var)
        self._provider_company_entry = ttk.Entry(self, takefocus=False, textvariable=self._provider_company_var)
        self._battery_capacity_entry = ttk.Entry(self, takefocus=False, textvariable=self._battery_capacity_var)
        self._battery_effectivity_entry = ttk.Entry(self, takefocus=False, textvariable=self._battery_effectivity_var)
        self._battery_threshold_entry = ttk.Entry(self, takefocus=False, textvariable=self._battery_threshold_var)
        self._battery_max_charge_rate_entry = ttk.Entry(self, takefocus=False, 
                                                        textvariable=self._battery_max_charge_rate_var)

        # CREATE BUTTONS
        self._solar_panels_setup_button = ttk.Button(self, text="Setup", 
                                                     width=20, takefocus=False,
                                                     command=self._open_solar_panels_setup)
        self._ev_setup_button = ttk.Button(self, text="Setup", width=20, takefocus=False)
        self._provider_supplement_setup_button = ttk.Button(self, text="Setup", 
                                                            width=20, takefocus=False,
                                                            command=self._open_supplement_setup)
        self._algorithm_vacation_setup_button = ttk.Button(self, text="Setup", width=20, takefocus=False)
        self._apply_button = ttk.Button(self, text="Apply", takefocus=False, command=self._apply_settings)

        # CREATE DROPDOWN
        self._grid_company_dropdown = ttk.Combobox(self, state='readonly', 
                                                   values=tuple(TARIFF_COMPANY.keys()), width=17, 
                                                   takefocus=False, textvariable=self._grid_company_var)
        self._algorithm_model_dropdown = ttk.Combobox(self, state='readonly',
                                                      values=('SmartBuy', 'GreenBuy'), width=17, 
                                                      takefocus=False, textvariable=self._algorithm_model_var)
        
        # PLACE COMPONENTS
        self._place_separators()
        self._place_household_section()
        self._place_extra_section()
        self._place_provider_section()
        self._place_battery_section()
        self._place_algorithm_section()

        # INIT FUNCTIONS
        self._update_variables(settings)

        
    def _update_variables(self, settings: dict[str, str]) -> None:
        """ Update ProfileTab with saved user settings from database 
        
        Args:
            settings: Saved user settings from database

        """
        self._address_var.set(settings['address'])
        self._city_var.set(settings['city'])
        self._postal_code_var.set(settings['postal'])
        self._country_var.set(settings['country'])
        self._solar_strategy_var.set(settings['solar_strategy'])
        self._solcast_key_var.set(settings['solcast_key'])
        self._solcast_resource_ids_list.set(settings['solcast_ids'])
        self._grid_company_var.set(settings['tariff_company'])
        self._provider_company_var.set(settings['provider'])
        self._basis_var.set(settings['basis'])
        self._prices_var.set(settings['prices'])
        self._battery_capacity_var.set(settings['capacity'])
        self._battery_effectivity_var.set(settings['effectivity'])
        self._battery_threshold_var.set(settings['threshold'])
        self._battery_max_charge_rate_var.set(settings['max_rate'])

    
    def _apply_settings(self) -> None:
        """ Apply settings and update database """
        db = Database()
        self._settings = self._create_settings()
        self._scheduler.update_settings(self._settings)
        self._update_variables(self._settings)

        if db.check_for_empty_table('settings'):
            db.insert_into_table('settings', tuple(self._settings.values()))
        else:
            db.update_table('settings', tuple(self._settings.values()))


    def _get_settings(self) -> dict[str, str]:
        """ Get saved user settings from database
            If no saved user settings, create new settings in memory
        
        Returns:
            Dict with user settings

        """
        db = Database()

        if not db.check_for_empty_table('settings'):
            return db.load_settings()
        
        return self._create_settings()


    def _create_settings(self) -> dict[str, str]:
        """ Create user settings dictionary in memory 
        
        Returns:
            Dict with user settings

        """
        address = self._address_var.get()
        city = self._city_var.get()
        postal = self._postal_code_var.get()
        country = self._country_var.get()

        if address and city and postal and country:
            geolocator = GeoLocator(address, city, postal, country)
            region = geolocator.locate('region')

            # GeoLocator can unexpectedly crash, so this is a 'fix' if no region found.
            if not region:
                if int(postal) < 5000:
                    price_area = 'DK2'
                else:
                    price_area = 'DK1'
            else:
                price_area = DANISH_REGIONS[geolocator.locate('region')]
        else:
            price_area = ""

        return {
            'address': address,
            'city': city,
            'postal': postal,
            'country': country,
            'price_area': price_area,
            'solar_strategy': self._solar_strategy_var.get(),
            'solcast_key': self._solcast_key_var.get(),
            'solcast_ids': self._solcast_resource_ids_list.get(),
            'tariff_company': self._grid_company_var.get(),
            'provider': self._provider_company_var.get(),
            'basis': self._basis_var.get(),
            'prices': self._prices_var.get(),
            'capacity': self._battery_capacity_entry.get(),
            'effectivity': self._battery_effectivity_entry.get(),
            'threshold': self._battery_threshold_entry.get(),
            'max_rate': self._battery_max_charge_rate_entry.get(),
            'model': self._algorithm_model_dropdown.get()
        }


    def _open_solar_panels_setup(self) -> None:
        """ Opens Solar Panels Setup Window on button press """
        SolarPanelsTop(self, self._solar_strategy_var,
                       self._solcast_key_var, self._solcast_resource_ids_list)
        

    def _open_supplement_setup(self) -> None:
        """ Opens SpotPrice Supplement Setup Window on button press """
        SupplementTop(self, self._basis_var, self._prices_var)


    def _place_separators(self) -> None:
        """ Place Separator components """
        self._vertical_separator.grid(row=0, column=2, rowspan=14, sticky=f'{tk.N}{tk.S}', padx=5)
        self._horizontal_separator_1.grid(row=5, column=0, columnspan=5, sticky=f'{tk.W}{tk.E}', pady=5)
        self._horizontal_separator_2.grid(row=9, column=0, columnspan=5, sticky=f'{tk.W}{tk.E}', pady=5)


    def _place_household_section(self) -> None:
        """ Place UI components related to Household Settings """
        # ROW 0, COLUMN 0 & 1
        self._household_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=10)

        # ROW 1, COLUMN 0 & 1
        self._address_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=3)
        self._address_entry.grid(row=1, column=1, padx=20, pady=3)

        # ROW 2, COLUMN 0 & 1
        self._city_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=3)
        self._city_entry.grid(row=2, column=1, padx=20, pady=3)

        # ROW 3, COLUMN 1 & 2
        self._postal_code_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=3)
        self._postal_code_entry.grid(row=3, column=1, padx=20, pady=3)

        # ROW 4, COLUMN 1 & 2
        self._country_label.grid(row=4, column=0, sticky=tk.W, padx=10, pady=3)
        self._country_entry.grid(row=4, column=1, padx=20, pady=3)


    def _place_extra_section(self) -> None:
        """ Place UI components related to Extra Household Settings """
        # ROW 6, COLUMN 0 & 1
        self._extra_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=10)

        # ROW 7, COLUMN 0 & 1
        self._solar_panels_label.grid(row=7, column=0, sticky=tk.W, padx=10, pady=3)
        self._solar_panels_setup_button.grid(row=7, column=1, padx=20, pady=3)

        # ROW 8, COLUMN 0 & 1
        self._ev_label.grid(row=8, column=0, sticky=tk.W, padx=10, pady=3)
        self._ev_setup_button.grid(row=8, column=1, padx=20, pady=3)


    def _place_provider_section(self) -> None:
        """ Place UI components related to Electric Utility Settings """
        # ROW 10, COLUMN 0 & 1
        self._provider_label.grid(row=10, column=0, columnspan=2, sticky=tk.W, padx=10)

        # ROW 11, COLUMN 0 & 1
        self._grid_company_label.grid(row=11, column=0, sticky=tk.W, padx=10, pady=3)
        self._grid_company_dropdown.grid(row=11, column=1, padx=20, pady=3)

        # ROW 12, COLUMN 0 & 1
        self._provider_company_label.grid(row=12, column=0, sticky=tk.W, padx=10, pady=3)
        self._provider_company_entry.grid(row=12, column=1, padx=20, pady=3)
        
        # ROW 13, COLUMN 0 & 1
        self._provider_supplement_label.grid(row=13, column=0, sticky=tk.W, padx=10, pady=5)
        self._provider_supplement_setup_button.grid(row=13, column=1, padx=20, pady=5)


    def _place_battery_section(self) -> None:
        """ Place UI components related to Battery Settings """
        # ROW 0, COLUMN 3 & 4
        self._battery_label.grid(row=0, column=3, columnspan=2, sticky=tk.W, padx=10)

        # ROW 1, COLUMN 3 & 4
        self._battery_capacity_label.grid(row=1, column=3, sticky=tk.W, padx=10, pady=3)
        self._battery_capacity_entry.grid(row=1, column=4, padx=60, pady=3)

        # ROW 2, COLUMN 3 & 4
        self._battery_effectivity_label.grid(row=2, column=3, sticky=tk.W, padx=10, pady=3)
        self._battery_effectivity_entry.grid(row=2, column=4, padx=60, pady=3)

        # ROW 3, COLUMN 3 & 4
        self._battery_threshold_label.grid(row=3, column=3, sticky=tk.W, padx=10, pady=3)
        self._battery_threshold_entry.grid(row=3, column=4, padx=60, pady=3)

        # ROW 4, COLUMN 3 & 4
        self._battery_max_charge_rate_label.grid(row=4, column=3, sticky=tk.W, padx=10, pady=3)
        self._battery_max_charge_rate_entry.grid(row=4, column=4, padx=60, pady=3)


    def _place_algorithm_section(self) -> None:
        """ Place UI components related to Algorithm Settings """
        # ROW 6, COLUMN 3 & 4
        self._algorithm_label.grid(row=6, column=3, columnspan=2, sticky=tk.W, padx=10)
        
        # ROW 7, COLUMN 3 & 4
        self._algorithm_model_label.grid(row=7, column=3, sticky=tk.W, padx=10, pady=3)
        self._algorithm_model_dropdown.grid(row=7, column=4, padx=60, pady=3)

        # ROW 8, COLUMN 3 & 4
        self._algorithm_vacation_label.grid(row=8, column=3, sticky=tk.W, padx=10, pady=3)
        self._algorithm_vacation_setup_button.grid(row=8, column=4, padx=60, pady=3)

        # ROW 10, COLUMN 3
        self._apply_button.grid(row=10, column=3, sticky=tk.W, padx=10, pady=5, ipadx=10, ipady=5)
    