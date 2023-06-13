## Here is the repository for Air-Pandas!!

There is a growing body of literature detailing the relationship between the level of air pollution and the demography in different neighborhoods of Los Angeles (e.g. Jiang and Yang 2022). Despite their substantial implications on the quality of life of millions of people, the majority of the discussions surrounding this issue have remained in an academic setting. In this project, we plan to increase accessibility to this body of knowledge. To do so, we will interpret the existing literature for demographic trends in Los Angeles and how they relate to real air quality records, create a database of historical Los Angeles air quality and demographic data, and visualize the relationship between demographic and air quality trends. These tasks will require working with large demographic and environmental datasets, creating and working with a SQL database, and communicating the findings through complex visualizations.


## API request

## SQLite Database Query and GUI

This project provides an interactive GUI to query and explore data from SQLite databases. It is developed with the intention to assist in analysis of air quality and census data.

## Introduction

The primary features of this project include:
1. An interactive GUI built with PySimpleGUI that allows users to select a SQLite database and perform operations like querying data from tables.
2. A `database_query.py` file containing several utility functions to interact with SQLite databases and query data. The functions include extracting all tables, fetching column names, creating index on columns for efficient querying, querying data from a table based on various parameters and more.
3. Functions to calculate air quality metrics, like the percentage of measurements that exceed a certain threshold.

## Project Structure

The main components of this project are:

##### Data Collection

- `aqs_request.py`: This file interacts with the Air Quality System (AQS) API to request and scrape air quality data. Require json files: (see `json` folder)
    - `search_goals.json` --- endpoints and parameter requirement for different Airdata requests
    - `param_descriptions.json` --- explanations on each parameters

Check [AQS API website](https://aqs.epa.gov/aqsweb/documents/data_api.html) for details. You can expand the request functionality by adding proper endpoints and parameters based on the information in the link. 

- `census_request.py`: This file interacts with the ACS5 US Census API to request the census data of our interest. 

These data collection functionality is demonstrated in the `AqsGUI` class and `CensusGUI` class in the `gui.py`.

##### Data Processing and SQLite database creation

- `acs5_metadata_cleaning` folder: This contains the raw metadata from *acs5* census database and the script `census_metadata_cleaning.py` to clean that. The raw metadata in .xlsx is also in the folder; running `census_metadata_cleaning.py` would output a cleaned table plus the json files used by `census_request.py` for request. (*no need to run it, json already in the `json` folder*)

Note: The issue with *acs5* data scraping is that the codes you pass in for requesting each variable across years are *NOT* consistent. We did substantial cleaning and text manipulation on the metadata to dump out structurized json files.

- `data_cleaning.py`: This file contains the functions that turn data requested from API into SQL database.
    - `database_creator.py` is an example on how to use the `data_cleaning.py` to create a custom SQLite database with the data scraped from AQI and acs5 APIs.

Note: a sample SQLite database showcasing the output is provided in `airpandas_1.7z`, you may use it to test the interaction and visualization modules.


##### Database Interaction 
- `database_query.py`: This file contains a collection of utility functions for interacting with the SQLite database. Look into that if you want to:
    - Get information about your database and tables
    - Query data based on time range or geographical location
    - Increase query speed by adding extra indexing

- `visualization.py`: This file contains multiple ways to visualize the data from the SQLite database. 

##### User Interface:

- `gui.py`: This file ... ; there are 3 classes:
    - `AqsGUI`: 
    - `CensusGUI`:
    - `dbGUI`:

- `main.py`: (not implemented that)





## How to Use

To use this application, you would need to have a SQLite database file in the root directory. Here are the steps to run the application:

1. Install the required dependencies using pip:

2. Run the `main.py` script to start the application:

3. The application will open a window asking you to select a SQLite database. Navigate to the location of your SQLite database file and select it.

4. Once a database is selected, the application will display a main menu where you can choose to perform various operations like querying data from a table.

5. Depending on your choice, the application will guide you through the process. For example, if you choose to query data from a table, the application will show you a list of all tables in the database. After selecting a table, you will be asked to select the columns you want to query, and enter the date range and optionally, a FIPS code.

## Data Structure

The data in the SQLite database is organized in tables. Each table has a unique set of columns. The application is built with special consideration for air quality and census data, with some functions tailored for such data. However, the application can be extended to accommodate other data types and structures.

In case of air quality and census data, some important columns include 'FIPS' code (unique identifier for geographical areas), 'sample_measurement' (measure of air quality), 'date_local' or 'Year' for date, 'latitude', 'longitude', etc. There are some special functions in `database_query.py` that are tailored to handle such data.

## Extending the Application




