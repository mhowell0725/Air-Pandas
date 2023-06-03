import pandas as pd
from sqlalchemy import create_engine

def add_fips_column(df, state_col_name, county_col_name):
    '''
    Add a column for the FIPS code to a DataFrame

    :param df: the DataFrame to add the column to
    :param state_col_name: the name of the column containing the state code
    :param county_col_name: the name of the column containing the county code
    '''

    df['FIPS'] = df[state_col_name].astype(str).str.zfill(2) + \
                df[county_col_name].astype(str).str.zfill(3)
    ## str.zfill(n): adds zeroes to the left of the string until it reaches a length of n
    return df

def add_year_column(df, date_col_name):
    pass


def process_chunk(chunk):
    '''
    Process a chunk of data from the EPA API *daily data* 

    :param chunk: a chunk of data from the EPA APi (pandas DataFrame)
    '''
    # Add FIPS code
    add_fips_column(chunk, 'state_code', 'county_code')
    
    # Calculate the number of measures per site and add it as a new column
    site_counts = chunk.groupby(['latitude', 'longitude']).size().rename('measures')
    chunk = chunk.merge(site_counts, on=['latitude', 'longitude'])
    
    return chunk


def process_csv_in_chunks(file_name, chunk_size, sql_engine, table_name):
    '''
    Process a CSV file (for air quality, now) in chunks and store the results in a SQL database

    :param file_name: the name of the CSV file to process
    :param chunk_size: the number of rows to process at a time
    :param sql_engine: the SQL engine to use to connect to the database
    :param table_name: the name of the table to store the data in

    '''

    chunk_iter = pd.read_csv(file_name, chunksize=chunk_size)
    
    for i, chunk in enumerate(chunk_iter):
        chunk = process_chunk(chunk)
        
        if i == 0:
            chunk.to_sql(table_name, sql_engine, if_exists='replace', index=False)
        else:
            chunk.to_sql(table_name, sql_engine, if_exists='append', index=False)