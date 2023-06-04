import sqlite3
import pandas as pd

def get_all_tables(sql_database):
    conn = sqlite3.connect(sql_database)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    conn.close()

    return [table[0] for table in tables]

def get_column_names(table_name, sql_database):
    conn = sqlite3.connect(sql_database)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    conn.close()

    return [column[1] for column in columns]

def query_table(sql_database, table_name, columns, start_date, end_date, fips=None):
    conn = sqlite3.connect(sql_database)

    # Initialize the WHERE clause with the date range
    if table_name == 'PM25':
        where_clause = f"date_local BETWEEN '{start_date}' AND '{end_date}'"
    else:
        where_clause = f"Year BETWEEN {start_date} AND {end_date}"

    # If a FIPS code is provided, add it to the WHERE clause
    if fips is not None:
        where_clause += f" AND FIPS = '{fips}'"

    df = pd.read_sql_query(f"""
        SELECT {', '.join(columns)}
        FROM {table_name}
        WHERE {where_clause}
        """, conn)

    conn.close()

    return df
