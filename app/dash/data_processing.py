import datetime
from asyncio import TaskGroup
from decimal import Decimal
from typing import Any

import pandas as pd
from pandas import DataFrame

from app.dash.crud.read_data_for_calculation import ResultsTradesRepository
from app.db.db_connection import db_dependency
from project_settings import setting

new_records: list[tuple[Any, ...]] = []


async def get_data(
        tickers: str,
        date_min: datetime.date,
        date_max: datetime.date
) -> DataFrame:

    global new_records
    async with TaskGroup() as group:
        for ticker in tickers:
            group.create_task(dp_service(ticker, date_min, date_max))
    df = pd.DataFrame(
        new_records,
        columns=[
            'date', 'ticker', 'expenses', 'shares', 'capitalization', 'price', 'monthly_balance'
        ]
    )
    new_records = []
    return df.sort_values('date')


async def dp_service(
        ticker: str,
        date_min: datetime.date,
        date_max: datetime.date
) -> None:
    shares = 0
    monthly_balance = Decimal(0)
    day = setting.MONTHLY_PURCHASE_DAY
    dividends = None
    sentinel = setting.LIMIT_OF_DAYS_FOR_PRICE_SEARCH

    async with db_dependency.session() as session:

        data = await ResultsTradesRepository(session).db_read_data_for_calculation(
            ticker,
            date_min,
            date_max,
            dividends_purchase_day_offset=setting.DIVIDENDS_PURCHASE_DAY_OFFSET,
        )
        for record in data:
            date, _, price, value = record
            dividends = value if not dividends else dividends
            expenses = Decimal(0)

            if dividends:
                if price:
                    income = dividends * shares
                    shares = shares + (income + monthly_balance) // price
                    monthly_balance = (income + monthly_balance) % price

                    dividends = None

            if day == date.day:
                if price:
                    expenses = setting.MONTHLY_INVESTMENTS
                    shares = shares + (setting.MONTHLY_INVESTMENTS + monthly_balance) // price
                    monthly_balance = (setting.MONTHLY_INVESTMENTS + monthly_balance) % price

                    day = setting.MONTHLY_PURCHASE_DAY
                    sentinel = setting.LIMIT_OF_DAYS_FOR_PRICE_SEARCH
                else:
                    day = (date + datetime.timedelta(days=1)).day
                    sentinel -= 1
                    if not sentinel:
                        break

            if not price:
                continue

            capitalization = shares * price

            new_records.append(
                (
                    date,
                    ticker,
                    expenses,
                    shares,
                    capitalization,
                    price,
                    monthly_balance
                )
            )
