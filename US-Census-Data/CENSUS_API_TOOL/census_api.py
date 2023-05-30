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
    # Load the variables and cleaned definitions from the JSON files
    variables = read_json(r'US-Census-Data\CENSUS_API_TOOL\json\variables.json')
    cleaned_definitions = read_json(r'US-Census-Data\CENSUS_API_TOOL\json\cleaned_definitions.json')

    # Get the codes for the specified category
    codes = variables[category]

    # Initialize an empty DataFrame to store the data
    df = pd.DataFrame()

    data = []

    # Query the data for each year
    for year in range(start_year, end_year + 1):
        # Construct the URL for the API request
        url = f"https://api.census.gov/data/{year}/acs/acs5/profile?get=NAME,{','.join(codes)}&for=county:*&in=state:06&key={get_api_key()}"

        # Send the API request and get the response
        response = requests.get(url)
        print("Querying data for year", year)

        # Convert the response to a DataFrame and append it to df
        year_df = pd.DataFrame(response.json()[1:], columns=response.json()[0])
        year_df['Year'] = year  # Add a column for the year
        data.append(year_df)

    # Concatenate the data for all years into a single DataFrame
    df = pd.concat(data, ignore_index=True)


    # Replace the column names with their cleaned definitions
    for column in df.columns:
        if column in cleaned_definitions:
            df.rename(columns={column: cleaned_definitions[column]}, inplace=True)

    print("Saving data to CSV file")

    # Save the DataFrame to a CSV file
    df.to_csv(f'census_data_{category}_{start_year}-{end_year}.csv', index=False)

    

def main():
    query_census_data(2010, 2021, 'PERCENTAGE under POVERTY LEVEL')

if __name__ == "__main__":
    main()