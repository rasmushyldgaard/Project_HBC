"""
Setup for setting up supplement to SpotPrice

Date:
    07-11-2023

"""

import tkinter as tk
from tkinter import ttk

WIDTH = 310
HEIGHT = 380

class SupplementTop(tk.Toplevel):
    """ Class for SpotPrice Supplement Setup """
    def __init__(self, parent: ttk.Frame, basis_var: tk.StringVar, prices_var: tk.StringVar):
        super().__init__(parent)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)

        # VARIABLES
        self._basis_var = basis_var
        self._prices_var = prices_var
        self._current_basis_var = tk.StringVar(value=basis_var.get())
        self._current_basis_var.trace('r', self._trace_basis)
        self._current_basis_var.trace('w', self._trace_basis)
        self._price_var = tk.StringVar()
        self._start_hour_var = tk.StringVar()
        self._end_hour_var = tk.StringVar()
        self._current_selected_price = ''

        # CREATE SEPARATOR
        self._horizontal_separator = ttk.Separator(self, orient='horizontal')

        # CREATE LABELS
        self._supplement_label = ttk.Label(self, text="SpotPrice Supplement", font=('Calibri', 20, 'bold'))
        self._basis_label = ttk.Label(self, text="Basis", font=('Calibri', 14, 'bold'))
        self._price_label = ttk.Label(self, text="Price (kr)", font=('Calibri', 14, 'bold'))
        self._start_hour_label = ttk.Label(self, text="Start Hour", font=('Calibri', 14, 'bold'))
        self._end_hour_label = ttk.Label(self, text="End Hour", font=('Calibri', 14, 'bold'))

        # CREATE ENTRIES
        self._price_entry = ttk.Entry(self, takefocus=False, textvariable=self._price_var)
        self._start_hour_entry = ttk.Entry(self, takefocus=False, textvariable=self._start_hour_var)
        self._end_hour_entry = ttk.Entry(self, takefocus=False, textvariable=self._end_hour_var)

        # CREATE BUTTONS
        self._add_price_button = ttk.Button(self, text="Add",
                                            width=10, takefocus=False,
                                            command=self._add_price)

        # CREATE DROPDOWN
        self._basis_dropdown = ttk.Combobox(self, state='readonly',
                                            width=17, values=('Flat', 'Hourly'),
                                            textvariable=self._current_basis_var,
                                            takefocus=False)
        
        # CREATE TREEVIEW
        self._hourly_supplement_view = ttk.Treeview(self, height=7, takefocus=False, selectmode='browse')
        self._hourly_supplement_view['columns'] = ("Price", "Start", "End")
        self._hourly_supplement_view.column("#0", width=0, stretch=False)
        self._hourly_supplement_view.column("Price", anchor=tk.W, width=100)
        self._hourly_supplement_view.column("Start", anchor=tk.W, width=100)
        self._hourly_supplement_view.column("End", anchor=tk.W, width=100)
        self._hourly_supplement_view.heading("Price", text="Price (kr)", anchor=tk.W)
        self._hourly_supplement_view.heading("Start", text="Start Hour", anchor=tk.W)
        self._hourly_supplement_view.heading("End", text="End Hour", anchor=tk.W)
        self._hourly_supplement_view.bind('<Motion>', 'break')
        self._hourly_supplement_view.bind('<ButtonRelease-1>', self._edit_price)
        self._hourly_supplement_view.bind('<Double-1>', self._delete_price)

        if self._current_basis_var.get() == 'Hourly':
            self._fill_hourly_supplement_view(prices_var)
        else:
            self._price_var.set(prices_var.get())

        self._place_components()
        self.protocol("WM_DELETE_WINDOW", self._update_prices)
        self.focus_force()
        self.grab_set()
        parent.wait_window(self)


    def _fill_hourly_supplement_view(self, prices: tk.StringVar) -> None:
        """ Fill the hourly supplement treeview with current hourly prices """
        supplement_prices = prices.get().split(',')
        if supplement_prices[0]:
            for price in supplement_prices:
                if price:
                    p = price.split('-')
                    self._hourly_supplement_view.insert('', tk.END, values=(p[0], p[1], p[2]))
                continue


    def _add_price(self) -> None:
        """ Add a price to treeview """
        price = self._price_var.get()
        start = self._start_hour_var.get()
        end = self._end_hour_var.get()

        if price and start and end:
            if self._current_selected_price:
                index = self._hourly_supplement_view.index(self._current_selected_price)
                self._hourly_supplement_view.delete(self._current_selected_price)
                self._hourly_supplement_view.insert('', index, values=(price, start, end))
                self._current_selected_price = ''
                self._hourly_supplement_view['selectmode'] = 'none'
                self._hourly_supplement_view['selectmode'] = 'browse'
            else:
                self._hourly_supplement_view.insert('', tk.END, values=(price, start, end))

            self._price_var.set('')
            self._start_hour_var.set('')
            self._end_hour_var.set('')


    def _edit_price(self, _) -> None:
        """ Edit price in treeview """
        self._current_selected_price = self._hourly_supplement_view.focus()

        if self._current_selected_price:
            items = self._hourly_supplement_view.item(self._current_selected_price)
            self._price_var.set(items['values'][0])
            self._start_hour_var.set(items['values'][1])
            self._end_hour_var.set(items['values'][2])
        

    def _delete_price(self, _) -> None:
        """ Delete price from treeview on double click """
        self._current_selected_price = self._hourly_supplement_view.focus()
        if self._current_selected_price:
            self._hourly_supplement_view.delete(self._current_selected_price)
            self._current_selected_price = ''

    
    def _update_prices(self) -> None:
        """ Update Supplement Basis and Prices when closing setup window """
        current_basis = self._current_basis_var.get()
        self._basis_var.set(current_basis)

        if current_basis == 'Flat':
            self._prices_var.set(self._price_var.get())
        else:
            prices = [self._hourly_supplement_view.item(parent)['values'] for parent \
                      in self._hourly_supplement_view.get_children()]
            price_str = ""
            for price in prices:
                price_str += f"{price[0]}-{price[1]}-{price[2]},"
            self._prices_var.set(price_str)
        self.destroy()
        

    def _place_components(self) -> None:
        """ Place UI components related to SpotPrice Supplement Settings """
        # ROW 0, COLUMN 0 & 1
        self._supplement_label.grid(row=0, column=0, columnspan=3, padx=30, pady=5)

        # ROW 1, COLUMN 0 & 1
        self._horizontal_separator.grid(row=1, column=0, columnspan=5, sticky=f'{tk.W}{tk.E}', pady=2)

        # ROW 2, COLUMN 0 & 1
        self._basis_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self._basis_dropdown.grid(row=2, column=1, sticky=tk.W, padx=30, pady=2)

        # ROW 3, COLUMN 0 & 1
        self._price_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self._price_entry.grid(row=3, column=1, sticky=tk.W, padx=30, pady=2)

        # ROW 4, COLUMN 0 & 1
        self._price_label.grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self._price_entry.grid(row=4, column=1, sticky=tk.W, padx=30, pady=2)

        # ROW 5, COLUMN 0 & 1
        self._start_hour_label.grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self._start_hour_entry.grid(row=5, column=1, sticky=tk.W, padx=30, pady=2)

        # ROW 6, COLUMN 0 & 1
        self._end_hour_label.grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self._end_hour_entry.grid(row=6, column=1, sticky=tk.W, padx=30, pady=2)

        # ROW 7, COLUMN 0 & 1
        self._add_price_button.grid(row=7, column=0, sticky=tk.W, padx=5, pady=2)

        # ROW 8, COLUMN 0 & 1
        self._hourly_supplement_view.grid(row=8, column=0, columnspan=5, sticky=tk.W, padx=5, pady=2)


    def _trace_basis(self, *args) -> None: # pylint: disable=unused-argument
        """ Callback to trace current Basis value """
        if self._current_basis_var.get() == 'Flat':
            self._start_hour_entry['state'] = 'disabled'
            self._end_hour_entry['state'] = 'disabled'
            self._add_price_button['state'] = 'disabled'
        else:
            self._start_hour_entry['state'] = 'normal'
            self._end_hour_entry['state'] = 'normal'
            self._add_price_button['state'] = 'normal'
