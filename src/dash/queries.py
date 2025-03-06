get_info = """
    SELECT date,ticker,expenses,shares,capitalization,price
    FROM processed_data 
    WHERE ticker = ANY (%(t)s)
    ORDER BY date;
"""
get_tickers = """
    SELECT date, ticker 
    FROM processed_data
    ORDER BY date;
"""
get_expenses = """
    SELECT DISTINCT date, expenses
    FROM processed_data
    ORDER BY date;
"""
