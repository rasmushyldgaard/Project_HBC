"""
Electricity Provider Companies in Denmark

Date:
    24-09-2023

"""

from datetime import time

PROVIDER_COMPANY = {
    "Vindstød": {
        "Price": {
            time(5, 0, 0): 0.0,
            time(9, 0, 0): 0.36,
            time(13, 0, 0): 0.2,
            time(22, 0, 0): 0.36,
            time(23, 59, 59): 0.2
        }
    }
}