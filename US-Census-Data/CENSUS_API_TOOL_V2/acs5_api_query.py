import requests
import json
import pandas as pd
import PySimpleGUI as sg


def get_api_key(file_name = "censusapikey.txt"):
    '''
    obtain the api key from a file

    if no such file exists, prompt the user to input the details and store it in the file

    :param file_name: the file name of the file containing email and api key
    :return: email and api key in a tuple
    '''
    try: 
        # read the first two lines of the file -- email and api key
        with open(file_name, "r") as file:
            api_key = file.readline().strip()

    except FileNotFoundError:
        # Prompt the user to enter their email and API key
        layout = [
            [sg.Text('Enter your API key for US census database')],
            [sg.Text('API Key', size =(15, 1)), sg.InputText()],
            [sg.Submit(), sg.Cancel()]
        ]

        window = sg.Window('Enter API Details', layout)

        event, values = window.read()
        window.close()

        if event == 'Submit':
            
            api_key = values[0]

            # Save the details to a file
            with open(file_name, "w") as file:
                
                file.write(api_key)

    return api_key


def read_json(filename):
    '''
    Helper function to read a JSON file
    '''
    with open(filename, 'r') as file:
        return json.load(file)
    


def query_census_data(start_year, end_year, category):
    '''
    Query the US Census API for data in the specified category for the specified years
    Store the output as a CSV file

    :param start_year: the first year to query
    :param end_year: the last year to query (inclusive)
    :param category: the category to query (e.g. 'race')
    '''

    # Load the JSON mappings
    category_code_dict = read_json('category_code.json')
    year_category_abbrev_dict = read_json('year_category_abbrev.json')

    df = pd.DataFrame()
    data = []

    # Query the data for each year
    for year in range(start_year, end_year + 1):
        year = str(year) # Convert year to string to use as a dictionary key

        # Ensure the category exists for the year
        if year not in year_category_abbrev_dict or category not in year_category_abbrev_dict[year]:
            print(f'No data for category "{category}" in year {year}')
            continue

        # Get the list of codes for the category in the year
        codes = category_code_dict[category][year]

        # Construct the URL for the API request
        url = f"https://api.census.gov/data/{year}/acs/acs5/profile?get=NAME,{','.join(codes)}&for=county:*&in=state:06&key={get_api_key()}"

        # Send the API request and get the response
        response = requests.get(url)
        print("Querying data for year", year)

        # Check for a successful response
        if response.status_code != 200:
            print(f'Request failed for year {year} with status code {response.status_code}')
            continue

        # Parse the response JSON into a DataFrame, assuming the first row is the header
        year_df = pd.DataFrame(response.json()[1:], columns=response.json()[0])

        year_df['Year'] = year  # Add a column for the year

        # Replace the column names with their abbreviations
        abbrevs = year_category_abbrev_dict[year][category]
        for code, abbrev in zip(codes, abbrevs):
            year_df.rename(columns={code: abbrev}, inplace=True)

        data.append(year_df)

    # Concatenate the data for all years into a single DataFrame
    df = pd.concat(data, ignore_index=True)

    print("Saving data to CSV file")

    # Save the DataFrame to a CSV file
    df.to_csv(f'census_data_{category}_{start_year}-{end_year}.csv', index=False)

def main():
    '''
    This is an example of how to use the functions in this file to query the US Census API
    Query the US Census API for data in each category for the years 2009 to 2021
    Store the output for each category as a separate CSV file
    '''
    
    # Load the year-category-abbrev mapping
    year_category_abbrev_dict = read_json('year_category_abbrev.json')

    # Get a list of all unique categories
    categories = set()
    for year in year_category_abbrev_dict:
        categories.update(year_category_abbrev_dict[year].keys())

    # Query data for each category
    for category in categories:
        print(f'Querying data for category "{category}"')
        query_census_data(2009, 2021, category)

if __name__ == "__main__":
    main()
