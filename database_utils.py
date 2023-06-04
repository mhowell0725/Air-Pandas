import sqlite3
import pandas as pd

def get_all_tables(sql_database):
    '''
    Returns a list of all tables in the database

    :param sql_database: the name of the SQL database to query
    '''
    conn = sqlite3.connect(sql_database)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    conn.close()

    return [table[0] for table in tables]

def get_column_names(table_name, sql_database):
    '''
    Returns a list of all columns in the table

    :param table_name: the name of the table to query
    :param sql_database: the name of the SQL database to query
    '''

    conn = sqlite3.connect(sql_database)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    conn.close()

    return [column[1] for column in columns]

def query_table(sql_database, table_name, columns, start_date, end_date, fips=None):
    '''
    Query the SQL database and return a pandas DataFrame

    :param sql_database: the name of the SQL database to query
    :param table_name: the name of the table to query
    :param columns: a list of columns to return
    :param start_date: the start date of the date range to query (either a year or a date in the format YYYY-MM-DD)
    :param end_date: the end date of the date range to query (either a year or a date in the format YYYY-MM-DD)
    :param fips: the FIPS code to query (optional)
    '''

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

def get_unique_sites(sql_database, table_name):
    conn = sqlite3.connect(sql_database)
    
    df = pd.read_sql_query(f"""
        SELECT DISTINCT latitude, longitude
        FROM {table_name}
        """, conn)
        
    conn.close()
    
    return df

# def get_measurement_percentage(sql_database, table_name, fips, threshold, date_range=None):
#     conn = sqlite3.connect(sql_database)

#     # Initialize the WHERE clause with the FIPS code
#     where_clause = f"FIPS = '{fips}'"

#     # If a date range is provided, add it to the WHERE clause
#     if date_range is not None:
#         where_clause += f" AND date_local BETWEEN '{date_range[0]}' AND '{date_range[1]}'"

#     # Query the total number of measurements
#     df_total = pd.read_sql_query(f"""
#         SELECT COUNT(*) as total_count
#         FROM {table_name}
#         WHERE {where_clause}
#         """, conn)

#     # Query the number of measurements that exceed the threshold
#     df_threshold = pd.read_sql_query(f"""
#         SELECT COUNT(*) as threshold_count
#         FROM {table_name}
#         WHERE {where_clause} AND sample_measurement > {threshold}
#         """, conn)

#     conn.close()

#     # Calculate the percentage of measurements that exceed the threshold
#     percentage = (df_threshold['threshold_count'][0] / df_total['total_count'][0]) * 100

#     ## print: calculation done on FIPS code: {fips}
#     print(f"calculation done on FIPS code: {fips}")

#     return percentage

def get_measurement_percentage(sql_database, table_name, fips, threshold, start_date=None, end_date=None):
    conn = sqlite3.connect(sql_database)

    # Initialize the WHERE clause with the FIPS code
    where_clause = f"FIPS = '{fips}'"

    # If a date range is provided, add it to the WHERE clause
    if start_date is not None and end_date is not None:
        where_clause += f" AND date_local BETWEEN '{start_date}' AND '{end_date}'"

    # Query the total number of measurements
    df_total = pd.read_sql_query(f"""
        SELECT COUNT(*) as total_count
        FROM {table_name}
        WHERE {where_clause}
        """, conn)

    # Query the number of measurements that exceed the threshold
    df_threshold = pd.read_sql_query(f"""
        SELECT COUNT(*) as threshold_count
        FROM {table_name}
        WHERE {where_clause} AND sample_measurement > {threshold}
        """, conn)

    conn.close()

    # Calculate the percentage of measurements that exceed the threshold
    if df_total['total_count'][0] == 0:
        percentage = None  # No measurements were taken in the given date range

        print(f"No measurements were taken in the given date range for FIPS code: {fips}")
    else:
        percentage = (df_threshold['threshold_count'][0] / df_total['total_count'][0]) * 100

        print(f"calculation done on FIPS code: {fips}")

    return percentage


