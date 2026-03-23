from currency_converter import CurrencyConverter
from datetime import date

REFERENCE_DATE = date(2025, 1, 2)  # Set a reference date for currency conversion

def convert_to_usd(row):
    c = CurrencyConverter()
    try:
        return c.convert(row["Amount"], row["Currency"], 'USD', date=REFERENCE_DATE)
    except Exception as e:
        print(f"Error converting {row['Amount']} {row['Currency']} to USD: {e}")
        return None