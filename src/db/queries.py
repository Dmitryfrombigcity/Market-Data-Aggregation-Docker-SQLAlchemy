results_of_trades = """
                    CREATE TABLE IF NOT EXISTS results_of_trades(
                    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    trade_date date,
                    ticker varchar,
                    closing_price numeric,
                    last_page int
                    );"""

insert_results_of_trades = """
                    INSERT INTO results_of_trades(
                    trade_date,
                    ticker,
                    closing_price,
                    last_page
                    ) VALUES (%s,%s,%s,%s);"""

dividends = """
                    CREATE TABLE IF NOT EXISTS dividends(
                    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    registry_closing_date date,
                    ticker varchar,
                    value numeric
                    );"""

insert_dividends = """
                    INSERT INTO dividends(
                    registry_closing_date,
                    ticker,
                    value
                    ) VALUES (%s,%s,%s);"""

insert_days_off_to_results_of_trades = """
                    WITH days_off AS(
                        SELECT missing_date::date, 'day_off'::varchar as day_off
                        FROM generate_series(
                            (SELECT min(trade_date) FROM results_of_trades),
                            (SELECT max(trade_date) FROM results_of_trades), 
                            interval '1 day') as missing_date
                        LEFT JOIN results_of_trades 
                            ON missing_date = trade_date
                        WHERE trade_date is NULL
                            )
                    INSERT INTO results_of_trades(trade_date, ticker)
                    SELECT missing_date, day_off 
                    FROM days_off;"""

check_for_updates = """
                    SELECT max(last_page) AS value
                    FROM results_of_trades
                    GROUP BY ticker
                    HAVING ticker = %s;"""

check_for_dividends = """
                    SELECT COUNT(*) AS value
                    FROM dividends
                    GROUP BY ticker
                    HAVING ticker = %s;"""

data_for_calculation = """
                    WITH temp AS(
                        SELECT trade_date, r.ticker, closing_price, value
                        FROM results_of_trades AS r
                        JOIN (
                            SELECT * FROM dividends 
                            WHERE ticker = %(ticker)s
                            ) AS d
                            ON trade_date  = registry_closing_date + %(dividends_purchase_day_offset)s
                        WHERE r.ticker = %(ticker)s OR r.ticker = 'day_off'
                        )
                    SELECT trade_date, r.ticker, r.closing_price, value
                    FROM results_of_trades AS r
                    LEFT JOIN temp USING(trade_date)
                    WHERE trade_date >= (
                        SELECT min(trade_date) 
                        FROM results_of_trades 
                        WHERE ticker = %(ticker)s
                        )
                        AND (r.ticker = %(ticker)s OR r.ticker = 'day_off')
                        ORDER BY trade_date;"""

processed_data = """     
                    CREATE TABLE  processed_data(
                    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    date date NOT NULL,
                    ticker varchar,
                    expenses numeric NOT NULL,
                    shares int NOT NULL,
                    capitalization numeric NOT NULL,
                    price numeric NOT NULL,
                    monthly_balance numeric NOT NULL
                    );"""

insert_processed_data = """
                    INSERT INTO processed_data(
                    date,
                    ticker,
                    expenses,
                    shares,
                    capitalization,
                    price,
                    monthly_balance
                    ) VALUES (%s,%s,%s,%s,%s, %s, %s);"""

get_next_record = """
                    SELECT trade_date, ticker, closing_price
                    FROM results_of_trades 
                    WHERE (ticker = %(ticker)s  OR ticker = 'day_off')
                    AND trade_date = %(date)s::date + 1;
                    """
truncate = """  
                    TRUNCATE TABLE {table};
                    """
