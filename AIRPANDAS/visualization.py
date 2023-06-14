
import pandas as pd
from sqlalchemy import create_engine

import sqlite3
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import plotly.express as px
import json


with open('AIRPANDAS\json\geojson-counties-fips.json', 'r') as file:
    counties = json.load(file)
    
# function to calculate proportion of times in a year there was a certan level of air quality

def calc_proportion(level, year):
    '''
    calculates the proportion of air quality readings in each county that is above a certain `level` over the span of a year.
    
    Args:
        level: string or int. choose from the following:
            "moderate": PM2.5 level ranging from 15 µg per cubic meter and above
            "unhealthy": PM2.5 level ranging from 30 µg per cubic meter and above
            int: aqi of whatever the int is or above
        year: the year for which we query the data
        
    Returns:
        a pandas data frame that contains the proportion of times a county experienced air quality above a certain `level`, as well as other variables necessary for plotting the air quality data.
    '''
    #set the air quality levels
    if level == "moderate":
        lower = 15
        
    elif level == "unhealthy":
        lower = 30
    
    else:
        lower = level
        
    #interact with the sql database to get the relevant data
    conn = sqlite3.connect('airpandas_1.sqlite')

    df = pd.read_sql_query(f"SELECT sample_measurement, FIPS, county FROM PM25 WHERE year = {year}", conn)

    conn.close()
        
    #calculate the proportion of measurements with PM2.5 concentration above the specified threshold
    r = list(df["FIPS"].unique())
    s = list(df["FIPS"].unique())
    j = 0
            
    for i in df["FIPS"].unique():
        s[j] = len(df["sample_measurement"][(lower <= df["sample_measurement"]) & (df["FIPS"] == i)])
        r[j] = len(df[df["FIPS"] == i])
        j += 1
            
    df1 = pd.DataFrame(df["FIPS"].unique(), columns = ["FIPS"])
    df1["values"] = [s / r for s, r in zip(s, r)]
    df1["county"] = list(df["county"].unique())
        
    return(df1)


def data_census(census_table, columns, year):
    '''
    queries desired variables from the relevant table in the airpandas_1 sqlite database in a given year
    
    Args:
        census_table: string. the table from the SQL database we want to work with.
        columns: list of strings. each string is a variable from the SQL database.
        year: int. the year for which we want to plot the data.
        
    Returns:
        a pandas dataframe containing the desired variables
    '''
    
    #interact with the sqlite database to retrieve the specified data
    conn = sqlite3.connect('airpandas_1.sqlite')

    df = pd.read_sql_query(f"SELECT {', '.join(columns)}, NAME, FIPS FROM {census_table} WHERE year = {year}", conn)

    conn.close()
    
    #clean the county names to fit the format of the future plot
    df["NAME"] = df["NAME"].str[:-19]
    
    if len(columns) == 1:
        df["values"] = df[columns[0]]
        return(df)
    
    else:
        df["values"] = df.iloc[:,0:len(columns)].sum(axis=1)
        return(df)
    
    
def add_aqi_trace(fig, df, variable, FIPS, county_name):
    '''
    adds a choropleth subplot to a plotly figure with county-level air quality data
    
    Args:
        fig: the figure we want to add a subplot to
        df: the data frame with air quality data in it
        variable: the air quality variable we want to display on the choropleth map
        FIPS: the FIPS codes associated with each county
        county_name: a column specifying the names of each county
    '''
    
    fig.add_trace(go.Choropleth(z = df[variable], 
                                geojson=counties, 
                                locations= df[FIPS],
                                text=df[county_name],
                                hovertemplate = "<b>County: %{text}</b><br><br>" + "value: %{z}<br>"
                                ),
                  row = 1, 
                  col = 2)
    
    fig.update_geos(
        fitbounds="locations", 
        visible=False
    )
    
    
def add_census_trace(fig, df, variable, variable_name, FIPS, county_name):
    
    '''
    adds a choropleth subplot to a plotly figure with county-level census data
    
    Args:
        fig: the figure we want to add a subplot to
        df: the data frame with census data in it
        variable: the census variable we want to display on the chropleth map
        FIPS: the fips codes are associated with each county
        county_name: a column specitying the names of each county
    '''
    
    fig.add_trace(go.Choropleth(z = df[variable], 
                                geojson=counties, 
                                locations= df[FIPS], 
                                text=df[county_name],
                                hovertemplate = "<b>County: %{text}</b><br><br>" + "value: %{z}<br>",
                                colorbar_x=0.45
                                ),
                  row = 1, 
                  col = 1)
    
    fig.update_geos(
        fitbounds="locations", 
        visible=False
    )
    

def create_side_comparison(level, year, census_table, census_columns):
    
    '''
    generates a figure comparing demographcs and air quality
    
    Args:
        level: an int or string giving the level of air quality index or above we want to include in the plot.
        year: int. the year for which we want to plot the data.
        census_table: string. the table from which we want to gather the census variable(s).
        census_columns: list of strings. the columns from the `census_table` we want to select.
        
    Returns:
        a plotly figure comparing the chosen demographics and air quality information in a given year
    '''
    
    rows = 1
    cols = 2
    fig = make_subplots(
        rows=rows, cols=cols,
        specs = [[{'type': 'choropleth'} for c in np.arange(cols)] for r in np.arange(rows)],
        subplot_titles = [f" {year} Census: {' + '.join(census_columns)}", f"Proportion of {year} with PM2.5 above level '{level}'"]
        )
    
    #plotting the air quality subplot
    add_aqi_trace(fig, calc_proportion(level, year), "values", "FIPS", "county")

    #plotting the census subplot
    add_census_trace(fig, data_census(census_table, census_columns, year), "values", "values", "FIPS", "NAME")
    
    fig.update_layout(coloraxis = {'colorscale':'viridis'})
    
    fig.show()

## A small show case of the functions here if you run this py file ##
def main():
    import database_query as dbq
    dbq.create_index('airpandas_1.sqlite', 'PM25', 'year')
    dbq.create_index('airpandas_1.sqlite', 'PM25', 'FIPS')
    dbq.create_index('airpandas_1.sqlite', 'PM25', ['date_local', 'FIPS'])

    # Compare air quality with educational attainment and income
    census_tables = ['Education', 'Income']
    census_columns = [['pct_bachelors_degree'], ['est_median_household_income']]
    year = 2020
    level = "unhealthy"

    for table, columns in zip(census_tables, census_columns):
        fig, _ = create_side_comparison(level, year, table, columns)
        fig.write_html(f"{table}_comparison_{year}.html") ## save the figure as html file


if __name__ == "__main__":
    main()
