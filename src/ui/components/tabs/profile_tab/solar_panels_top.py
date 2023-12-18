"""
Setup for selecting SolarStrategy and setting up SolCast API

Date:
    06-11-2023

"""

import tkinter as tk
from tkinter import ttk


WIDTH = 310
HEIGHT = 370

class SolarPanelsTop(tk.Toplevel):
    """ Class for Solar Panels Setup """
    def __init__(self, parent: ttk.Frame, solar_strategy_var: tk.StringVar,
                 solcast_key_var: tk.StringVar, solcast_resource_ids_list: tk.StringVar):
        super().__init__(parent)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)

        # VARIABLES
        self._current_resource_id_var = tk.StringVar()
        self._current_resource_id_var.trace('w', self._trace_current_resource_id)
        self._solcast_resource_ids_list = solcast_resource_ids_list
        
        # CREATE SEPARATOR
        self._horizontal_separator = ttk.Separator(self, orient='horizontal')
        self._horizontal_separator_2 = ttk.Separator(self, orient='horizontal')

        # CREATE LABELS
        self._solar_panels_label = ttk.Label(self, text="Solar Panels", font=('Calibri', 20, 'bold'))
        self._enable_solar_panels_label = ttk.Label(self, text="Enable Solar Panels", font=('Calibri', 14, 'bold'))
        self._solar_strategy_label = ttk.Label(self, text="SolarStrategy", font=('Calibri', 14, 'bold'))
        self._solcast_key_label = ttk.Label(self, text="SolCast API Key", font=('Calibri', 14, 'bold'))
        self._solcast_resource_id_label = ttk.Label(self, text="SolCast Resource ID", font=('Calibri', 14, 'bold'))

        # CREATE ENTRIES
        self._solcast_key_entry = ttk.Entry(self, takefocus=False, textvariable=solcast_key_var)
        self._solcast_resource_id_entry = ttk.Entry(self, takefocus=False, textvariable=self._current_resource_id_var)

        # CREATE BUTTONS
        self._add_resource_id_button = ttk.Button(self, text="Add", state='disabled',
                                                  width=10, takefocus=False,
                                                  command=self._add_resource_id)

        # CREATE DROPDOWN
        self._solar_strategy_dropdown = ttk.Combobox(self, state='readonly', 
                                                     width=17, values=('Sell All', 'Save All'),
                                                     textvariable=solar_strategy_var,
                                                     takefocus=False)
        
        # CREATE TREEVIEW
        self._solcast_resource_id_view = ttk.Treeview(self, height=8, takefocus=False, selectmode='browse')
        self._solcast_resource_id_view['columns'] = "ID"
        self._solcast_resource_id_view.column("#0", width=0, stretch=False)
        self._solcast_resource_id_view.column("ID", anchor=tk.W, stretch=True)
        self._solcast_resource_id_view.heading("ID", text="ID", anchor=tk.W)
        self._fill_resource_id_view(self._solcast_resource_ids_list)
        self._solcast_resource_id_view.bind('<Motion>', 'break')
        self._solcast_resource_id_view.bind('<Double-1>', self._delete_resource_id)
        

        # INIT FUNCTIONS
        self._place_components()
        self.protocol("WM_DELETE_WINDOW", self._update_resource_ids)
        self.focus_force()
        self.grab_set()
        parent.wait_window(self)
    

    def _fill_resource_id_view(self, resource_ids: tk.StringVar) -> None:
        """ Fill the resource ID treeview with current resource_ids """
        res_ids = resource_ids.get().split(',')
        if res_ids[0]:
            for res_id in res_ids:
                self._solcast_resource_id_view.insert('', tk.END, values=(res_id)) # type: ignore


    def _add_resource_id(self) -> None:
        """ Add a resource ID to treeview """
        resource_id = self._current_resource_id_var.get()
        if resource_id:
            self._solcast_resource_id_view.insert('', tk.END, values=(resource_id)) # type: ignore
            self._current_resource_id_var.set('')


    def _delete_resource_id(self, _) -> None:
        """ Delete selected resource ID from treeview on double click """
        selected_id = self._solcast_resource_id_view.selection()
        if selected_id:
            self._solcast_resource_id_view.delete(selected_id[0])


    def _update_resource_ids(self) -> None:
        """ Update resource ID variable when closing setup window """
        resource_ids_list = [self._solcast_resource_id_view.item(parent)['values'][0] for parent \
                             in self._solcast_resource_id_view.get_children()]
        self._solcast_resource_ids_list.set(','.join(resource_ids_list))
        self.destroy()


    def _place_components(self) -> None:
        """ Place UI components related to Solar Panels Settings """
        # ROW 0, COLUMN 0 & 1
        self._solar_panels_label.grid(row=0, column=0, columnspan=2, pady=5)

        # ROW 1, COLUMN 0 & 1
        self._horizontal_separator.grid(row=1, column=0, columnspan=5, sticky=f'{tk.W}{tk.E}', pady=2)

        # ROW 2, COLUMN 0 & 1
        self._solar_strategy_label.grid(row=2, column=0, sticky=tk.W, padx=5)
        self._solar_strategy_dropdown.grid(row=2, column=1, sticky=tk.W, padx=20)

        # ROW 3, COLUMN 0 & 1
        self._solcast_key_label.grid(row=3, column=0, sticky=tk.W, padx=5)
        self._solcast_key_entry.grid(row=3, column=1, sticky=tk.W, padx=20)

        # ROW 4, COLUMN 0 & 1
        self._horizontal_separator_2.grid(row=4, column=0, columnspan=5, sticky=f'{tk.W}{tk.E}', pady=2)

        # ROW 5, COLUMN 0 & 1
        self._solcast_resource_id_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
        # ROW 6, COLUMN 0 & 1 & 2
        self._solcast_resource_id_entry.grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self._add_resource_id_button.grid(row=6, column=1, sticky=tk.W, pady=2)

        # ROW 7, COLUMN 0 & 1
        self._solcast_resource_id_view.grid(row=7, column=0, columnspan=5, sticky=tk.W, padx=5, pady=2, ipadx=49)


    def _trace_current_resource_id(self, *args) -> None: # pylint: disable=unused-argument
        """ Callback to trace input text in entry for resource ID """
        if self._current_resource_id_var.get():
            self._add_resource_id_button['state'] = 'normal'
        else:
            self._add_resource_id_button['state'] = 'disabled'


