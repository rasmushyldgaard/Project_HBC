"""
Run HomeBatteryController

Date:
    16-10-2023

Example:
    >>> python main.py

"""

import os
from ui import Application

if __name__ == "__main__":
    current_os = os.name
    app = Application(current_os)
    app.mainloop()
    