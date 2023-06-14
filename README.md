
# Welcome to AIRPANDAS!!

AIRPANDAS is a Python-based project that interacts with the Air Quality System (AQS) API and the ACS5 US Census API to collect, process, and visualize air quality and census data. It provides a suite of tools to help you create custom SQLite databases, interact with them, and visualize your data in meaningful ways.

With AIRPANDAS, you can:

- *Collect Data*: Use our built-in scripts to gather air quality and census data directly from the AQS and ACS5 APIs.
- *Process Data*: Clean and structure your data with our data processing scripts, and create your own SQLite databases.
- *Interact with Databases*: Utilize our utility functions to query your databases, get information about your tables, and optimize your queries.
- *Visualize Data*: Bring your data to life with our visualization tools, and gain insights by seeing air quality and census plot side-by-side!

AIRPANDAS also includes a user-friendly GUI that integrates all these features, making it easy for users of all levels to leverage the power of it. 


### Briefing

All python scrips are under the `AIRPANDS` folder. In short, it centered around populating and interacting with an SQLite datbase.
- Obtain the metadata from AQS Air Quality database and ACS5 Census database; create JSON files to store cleaned metadata. (examples see `acs5_metadata_cleaning` folder)
- The `aqs_request.py` and `census_request.py` scripts interact with the respective APIs to collect data. These scripts use JSON files to specify the endpoints and parameters for the API requests. 
- The `data_cleaning.py` cleaned the data and create a SQLite database to store it.
- The `database_query.py` script provides utility functions for interacting with the SQLite database, such as querying data based on time range or geographical location, and adding indexing to increase query speed.
- The `visualization.py` script uses the data from the SQLite database to create visualizations.
- The `gui.py` generate user interface to demonstrate how to use the data collection, database interaction, and visualization features.

## How to Use

Basically, run the `main.py` file under *root repository*. (The file is inside the `AIRPANDAS` folder, but when you run it, your base repository should be just outside, in its **parent** folder.)

To test all feature of this application, you would need to prepare:

- For *Air Quality Request*, an email and corresponding APIkey for the AQS database; You can obtain this by access the following url: `https://aqs.epa.gov/data/api/signup?email={youremail}`. Replace *{youremail}* (including the bracket outside) with your actual email address and you'll receive an APIkey.
- For *Census Request*, get API key from [here](https://api.census.gov/data/key_signup.html)
- For *Database Query* features, you'll need to locate a proper SQLite database file. We've provide a sample database with PM2.5 measurement and various census data. Unzip the `airpandas_1.7z` to get the sample sqlite database, or create your own using the code we provided.

Here are the steps to run the application:

1. Install the required dependencies. The `requirement.txt` includes all the packages; you can try `pip install -r requirements.txt`

2. Run the `main.py` script at the root repository to start the GUI: Navigate to the root directory in your terminal and run `python AIRPANDAS/main.py"`.

3. The application will open a window asking you to select the feature you want to try out. Follow the guidance in the GUI interface and it should work. 

4. If you created and plot and tables during the process, they will by default be stored in the root repository.
 
Some notes:
    - You will be prompted to input your apikeys when needed. They will be stored at the base repository once you enter it, and won't change until you delete or modify the file. (*you may want to check if they are correct in case you consistantly fail to scarp data*) 
    - For *Air Quality Request*, the details about AQS database is [here](https://aqs.epa.gov/aqsweb/documents/data_api.html)
    - When query or plot data from our sample database, you may find certain variables to be missing in certain years. Check the `census_metadata_cleaned.xlsx` in acs5_metadata to see if centain variable is avaliable in certain year. 


## Detailed Project Structure

##### Data Collection

- `aqs_request.py`: This file interacts with the Air Quality System (AQS) API to request and scrape air quality data. Require JSON files: (see `json` folder)
    - `search_goals.json` --- endpoints and parameter requirement for different Airdata requests
    - `param_descriptions.json` --- explanations on each parameters

Check [AQS API website](https://aqs.epa.gov/aqsweb/documents/data_api.html) for details. You can expand the request functionality by adding proper endpoints and parameters based on the information in the link. 

- `census_request.py`: This file interacts with the ACS5 US Census API to request the census data of our interest. It interact with the rest json files in the `json` folder. 

These data collection functionality is demonstrated in the `AqsGUI` class and `CensusGUI` class in the `gui.py`.

##### Data Processing and SQLite database creation

- `acs5_metadata_cleaning` folder: This contains the raw metadata from *acs5* census database and the script `census_metadata_cleaning.py` to clean that. The raw metadata in .xlsx is also in the folder; running `census_metadata_cleaning.py` would output a cleaned table plus the json files used by `census_request.py` for request. (*no need to run it, json already in the `json` folder*)

Note: The issue with *acs5* data scraping is that the codes you pass in for requesting each variable across years are *NOT* consistent. We did substantial cleaning and text manipulation on the metadata to dump out structurized json files.

- `data_cleaning.py`: This file contains the functions that turn data requested from API into SQL database.
    - `database_creator.py` is an example on how to use the `data_cleaning.py` to create a custom SQLite database with the data scraped from AQI and acs5 APIs. Not interacting with the main part of the project

Note: a sample SQLite database showcasing the output is provided in `airpandas_1.7z`, you may use it to test the interaction and visualization modules.


##### Database Interaction 
- `database_query.py`: This file contains a collection of utility functions for interacting with the SQLite database. Look into that if you want to:
    - Get information about your database and tables
    - Query data based on time range or geographical location
    - Increase query speed by adding extra indexing

- `visualization.py`: This file contains multiple ways to visualize the data from the SQLite database. Interact with `dbGUI` classes plotting features in `gui.py`.

##### User Interface:

- `gui.py`: This file implement the major functions above into GUI ; there are 3 classes:
    - `AqsGUI`: show how to obtain data from AQS Air quality API
    - `CensusGUI`: show how to obtain data from acs5 census API
    - `dbGUI`: query or plot data given a sqlite database with tables storing AQS and acs5 data

- `main.py`: Use this file calls the 3 classes in `gui.py` to test the functionality of our code.

