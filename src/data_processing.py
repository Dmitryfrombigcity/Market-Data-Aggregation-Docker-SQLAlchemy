from datetime import timedelta
from decimal import Decimal
from typing import cast

from project_settings import setting
from src.db.crud import db_read, db_update
from src.db.queries import data_for_calculation, insert_processed_data
from src.db.schemas import Record


async def data_processing(ticker: str) -> None:
    """processing of data according to specified settings"""

    data = cast(list[Record], await db_read(
        data_for_calculation, {
            'ticker': ticker,
            'dividends_purchase_day_offset': setting.DIVIDENDS_PURCHASE_DAY_OFFSET,
        }
    ))  # to satisfy mypy

    shares = monthly_balance = expenses = Decimal(0)
    day = setting.MONTHLY_PURCHASE_DAY
    dividends = None
    sentinel = setting.LIMIT_OF_DAYS_FOR_PRICE_SEARCH

    for record in data:
        dividends = record.value if not dividends else dividends
        price = record.closing_price
        date = record.trade_date

        if dividends:
            if price:
                income = dividends * shares
                shares = shares + (income + monthly_balance) // price
                monthly_balance = (income + monthly_balance) % price

                dividends = None

        if day == date.day:
            if price:
                expenses += setting.MONTHLY_INVESTMENTS
                shares = shares + (setting.MONTHLY_INVESTMENTS + monthly_balance) // price
                monthly_balance = (setting.MONTHLY_INVESTMENTS + monthly_balance) % price

                day = setting.MONTHLY_PURCHASE_DAY
                sentinel = setting.LIMIT_OF_DAYS_FOR_PRICE_SEARCH
            else:
                day = (date + timedelta(days=1)).day
                sentinel -= 1
                if not sentinel:
                    break

        if not price:
            continue

        capitalization = shares * price

        new_record = date, ticker, expenses, shares, capitalization, price, monthly_balance
        await db_update(insert_processed_data, (new_record,))
