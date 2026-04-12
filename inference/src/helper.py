from currency_converter import CurrencyConverter
from datetime import date


REFERENCE_DATE = date(2025, 1, 2)  # Set a reference date for currency conversion


def convert_to_usd(row, column_name, reference_date=REFERENCE_DATE):
    c = CurrencyConverter()
    try:
        return c.convert(row[column_name], row["Currency"], 'USD', date=reference_date)
    except Exception as e:
        print(f"Error converting {row[column_name]} {row['Currency']} to USD: {e}")
        return None
