"""
Helperfunction for putting text inside a disabled Tkinter Text Widget
"""

import tkinter as tk
from typing import Any

def write_text(text: tk.Text, value: Any) -> tk.Text:
    """ Write the given value into a Tk Text object

    Args:
        text: A Tk Text object
        value: Any value

    Returns:
        Changed Tk Text object with value written

    """
    text['state'] = 'normal'
    text.delete('1.0', tk.END)
    text.insert(tk.END, f'{value}')
    text['state'] = 'disabled'
    return text
