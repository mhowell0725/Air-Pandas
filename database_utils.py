import sqlite3
import pandas as pd
import plotly.express as px
import json

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

def get_unique_fips(sql_database, table_name):
    conn = sqlite3.connect(sql_database)
    
    df = pd.read_sql_query(f"""
        SELECT DISTINCT FIPS
        FROM {table_name}
        """, conn)
        
    conn.close()
    
    return df


# def get_measurement_percentage(sql_database, table_name, fips, threshold, start_date=None, end_date=None):
#     conn = sqlite3.connect(sql_database)

#     # Initialize the WHERE clause with the FIPS code
#     where_clause = f"FIPS = '{fips}'"

#     # If a date range is provided, add it to the WHERE clause
#     if start_date is not None and end_date is not None:
#         where_clause += f" AND date_local BETWEEN '{start_date}' AND '{end_date}'"

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
#     if df_total['total_count'][0] == 0:
#         percentage = None  # No measurements were taken in the given date range

#         print(f"No measurements were taken in the given date range for FIPS code: {fips}")
#     else:
#         percentage = (df_threshold['threshold_count'][0] / df_total['total_count'][0]) * 100

#         print(f"calculation done on FIPS code: {fips}")

#     return percentage

### optimize access time: INDEXING

def get_measurement_percentage(sql_database, table_name, fips, threshold, start_date=None, end_date=None):
    conn = sqlite3.connect(sql_database)

    # Initialize the WHERE clause with the FIPS code
    where_clause = f"FIPS = '{fips}'"

    # If a date range is provided, add it to the WHERE clause
    if start_date is not None and end_date is not None:
        ## determine the format of the date -- if they are integers, then they are years
        if isinstance(start_date, int) and isinstance(end_date, int):
            where_clause += f" AND Year BETWEEN {start_date} AND {end_date}"
        else:
            where_clause += f" AND date_local BETWEEN '{start_date}' AND '{end_date}'"

    # Query the total number of measurements and the number of measurements that exceed the threshold
    df = pd.read_sql_query(f"""
        SELECT 
            COUNT(*) as total_count,
            SUM(CASE WHEN sample_measurement > {threshold} THEN 1 ELSE 0 END) as threshold_count
        FROM {table_name}
        WHERE {where_clause}
        """, conn)

    conn.close()

    # Calculate the percentage of measurements that exceed the threshold
    if df['total_count'][0] == 0:
        percentage = None  # No measurements were taken in the given date range
        print(f"No measurements were taken in the given date range for FIPS code: {fips}")
    else:
        percentage = (df['threshold_count'][0] / df['total_count'][0]) * 100
        print(f"Calculation done on FIPS code: {fips}")

    return percentage



## indexing the database -- create index function

def create_index(sql_database, table_name, columns):
    '''
    Create an index on the given table and columns
    
    :param sql_database: the name of the SQL database to query
    :param table_name: the name of the table to query
    :param columns: a list of columns to return

    '''
    conn = sqlite3.connect(sql_database)
    c = conn.cursor()

    # If columns is a string, make it a single-item list
    if isinstance(columns, str):
        columns = [columns]

    column_str = ", ".join(columns)
    c.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{'_'.join(columns)} ON {table_name} ({column_str})")
    conn.commit()
    conn.close()


def ploty_census(sql_database, census_table,census_var,year):

    conn = sqlite3.connect(sql_database)

    df = pd.read_sql_query(f"x")
                           
    pass


# def analyze_air_quality(year_range, threshold, sql_database, table_name, geojson_file ,state = None,):




def get_county_fips(sql_database, table_name, state=None, state_column='state', county_column='county', fips_column='FIPS'):
    conn = sqlite3.connect(sql_database)

    # Add a WHERE clause if a state is specified
    where_clause = f"WHERE {state_column} = '{state}'" if state else ''

    df_counties = pd.read_sql_query(f"SELECT DISTINCT {fips_column}, {county_column} FROM {table_name} {where_clause}", conn)
    conn.close()

    return df_counties

def air_threshold_percentages(df_counties, sql_database, table_name, threshold, begin_year=2009, end_year=2021):
    percentages = []
    for fips, county in df_counties.values:
        percentage = get_measurement_percentage(sql_database, table_name, fips, threshold, begin_year, end_year)
        percentages.append((fips, county, percentage))

    # Create a DataFrame from the percentages data
    df_percentages = pd.DataFrame(percentages, columns=['FIPS', 'County', 'Percentage'])
    return df_percentages


def plot_air_quality(df, geojson_file='geojson-counties-fips.json'):
    # Load GeoJSON file
    with open(geojson_file) as response:
        counties = json.load(response)

    # Define function to plot choropleth map
    fig = px.choropleth(df, geojson=counties, locations= 'FIPS', color='Percentage',
                        color_continuous_scale="Viridis",
                        scope="usa",
                        labels={'Percentage': 'Percentage of Unhealthy Air Quality'},
                        hover_name= 'County',
                        hover_data={'FIPS': False})
    fig.update_geos(
        fitbounds="locations", 
        visible=False
    )
    fig.show()



