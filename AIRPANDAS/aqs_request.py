import requests
import json
import PySimpleGUI as sg
from datetime import datetime, timedelta
import time
import pandas as pd

## this is the base url for the aqs api, and functions handle the request for the api
base_url = "https://aqs.epa.gov/data/api/"

def get_api_key(file_name = "aqsEmailKey.txt"):
    '''
    obtain the email and api key from a file
    require the first line to be email and second line to be api key

    if no such file exists, prompt the user to input the details and store it in the file

    :param file_name: the file name of the file containing email and api key
    :return: email and api key in a tuple
    '''
    try: 
        # read the first two lines of the file -- email and api key
        with open(file_name, "r") as file:
            email = file.readline().strip()
            api_key = file.readline().strip()

    except FileNotFoundError:
        # Prompt the user to enter their email and API key
        layout = [
            [sg.Text('Enter your email and API key for the EPA AQS database')],
            [sg.Text('Email', size =(15, 1)), sg.InputText()],
            [sg.Text('API Key', size =(15, 1)), sg.InputText()],
            [sg.Submit(), sg.Cancel()]
        ]

        window = sg.Window('Enter API Details', layout)

        event, values = window.read()
        window.close()

        if event == 'Submit':
            email = values[0]
            api_key = values[1]

            # Save the details to a file
            with open(file_name, "w") as file:
                file.write(email + "\n")
                file.write(api_key)

    return email, api_key


def load_serach_goals(file_name = "Air_quality_query\EQS_API_TOOL\json\search_goals.json"):
    '''
    load the endpoint listing from a json file
    :param file_name: the file name of the file containing endpoint listing
    :return: endpoint listing in a dictionary
    '''
    with open(file_name, "r") as file:
        goals_list = json.load(file)

    return goals_list

## Check json file for endpoint and parameters for request
def get_endpoint(goal):
    '''
    Based on user input, find the endpoint where the data is located
    :param goal: the goal of the request (e.g. "Daily by State")

    used function:
    load_serach_goals()
    '''
    goal_list = load_serach_goals()
    
    ## see if the goal is in the list
    if goal not in goal_list:
        raise ValueError("Invalid goal entered. Please make sure you're entering a valid option from the filters list.")
    
    ## if the goal is in the list, return the endpoint
    
    return goal_list[goal]["endpoint"]

def get_params(goal):
    '''
    Based on user input, find the required parameters

    used function:
    load_serach_goals()

    return a list of parameters *requirements*
    '''
    goal_list = load_serach_goals()
    
    if goal not in goal_list:
        raise ValueError("Invalid goal entered. Please make sure you're entering a valid option from the filters list.")
    
    return goal_list[goal]["parameters"]

def load_param_descriptions(file_name = "Air_quality_query\EQS_API_TOOL\json\param_descriptions.json"):
    '''
    load the parameter descriptions from a json file
    :param file_name: the file location containing parameter descriptions
    :return: parameter descriptions in a dictionary
    '''

    with open(file_name, 'r') as file:
        param_descriptions = json.load(file)
    return param_descriptions


def complete_params(params_requirement, input_values = None):
    '''
    Complete the parameters for the request
    return a dictionary of parameters that can be passed in to request directly

    used function:
    get_api_key()
    get_params()
    '''
    ## EQS API requires email and api key to be passed in as parameters
    email, api_key = get_api_key()

    params = {
        "email" : email,
        "key": api_key,
    }

    if input_values != None:
        for parameters in params_requirement:
            params[parameters] = input_values[parameters]

    return params

def get_data(goal,params):
    '''
    Complete request pull from AQS API with a give goal
    :param goal: the goal of the request (e.g. "Daily by State")

    return a request object of the data --- to be converted in data_processing

    used function:
    get_endpoint()
    get_params()
    complete_params()
    '''
    endpoint = get_endpoint(goal)

    response = requests.get(base_url + endpoint, params = params)

    #debug print
    #print(response.url)
    
    return response

### utility functions for data processing -- convert api response to dataframe and csv file


def convert_to_dataframe(api_response):
    """
    Convert the API response data (JSON format) to a pandas DataFrame.

    :param api_response: The JSON data received from the EPA AQS API.
    :return: A pandas DataFrame containing the data.
    """
    # Extract the relevant data from the API response and convert it to a DataFrame.
    # For example:
    data = api_response['Data']
    dataframe = pd.DataFrame(data)
    
    return dataframe

def save_to_file(dataframe, file_name, file_format="csv"):
    """
    Save the data in a pandas DataFrame to a specified file format (CSV or Excel).

    :param dataframe: The pandas DataFrame containing the data.
    :param file_name: The name of the file to save the data to.
    :param file_format: The format of the file (default is "csv").
    """
    if file_format.lower() == "csv":
        dataframe.to_csv(file_name, index=False)
    elif file_format.lower() == "excel":
        dataframe.to_excel(file_name, index=False)
    else:
        raise ValueError("Invalid file format. Supported formats are 'csv' and 'excel'.")


### From here on, the code is for interacting with the AQS API when *USER given* parameters with datatime


def is_date_in_range(bdate, edate, min_date, max_date):
    '''
    Check whether bdate and edate are within the allowed range and in the correct format

    :param bdate: the start date as a string in the format 'yyyymmdd'
    :param edate: the end date as a string in the format 'yyyymmdd'
    :param min_date: the earliest allowed date as a string in the format 'yyyymmdd'
    :param max_date: the latest allowed date as a string in the format 'yyyymmdd'
    :return: boolean indicating whether both dates are within the range and in the correct format
    '''

    try:
        bdate_obj = datetime.strptime(bdate, '%Y%m%d')
        edate_obj = datetime.strptime(edate, '%Y%m%d')
        min_date_obj = datetime.strptime(min_date, '%Y%m%d')
        max_date_obj = datetime.strptime(max_date, '%Y%m%d')

        return min_date_obj <= bdate_obj <= max_date_obj and min_date_obj <= edate_obj <= max_date_obj

    except ValueError:
        return False

def choose_query_strategy(params):
    """
    Choose a query strategy based on the parameters.

    :param params: Dictionary with the parameters.
    :return: The chosen condition.
    """
    bdate_str = params.get('bdate')
    edate_str = params.get('edate')

    # Check if bdate and edate are missing
    if not bdate_str or not edate_str:
        return "condition 1"
    ## note condition 1 is NOT implemented in execute_query_strategy, 
    ## i.e. nothing special will happen if bdate and edate are missing, and reqeust happen once with parameters as is

    try:
        # Convert the strings to datetime objects
        bdate = datetime.strptime(bdate_str, '%Y%m%d')
        edate = datetime.strptime(edate_str, '%Y%m%d')

        # Calculate the difference between the two dates
        difference = edate - bdate
        days_difference = difference.days

        # Validate the dates
        min_date = datetime.strptime('19800101', '%Y%m%d')
        max_date = datetime.today()

        if bdate < min_date or edate < min_date:
            raise ValueError('Date cannot be before 1980-01-01.')
        if bdate > max_date or edate > max_date:
            raise ValueError('Date cannot be in the future.')
        
        if edate < bdate:
            raise ValueError('End date cannot be before begin date.')

        # Compare the difference to different periods
        if days_difference <= 90:  # 3 months
            return "condition 2"
        elif days_difference <= 1825:  # 5 years
            return "condition 3"
        elif days_difference <= 3650:  # 10 years
            print("Warning: Large date range may result in slower performance.")
            return "condition 3"
        else:
            raise ValueError('Date range cannot be longer than 10 years.')

    except ValueError as e:
        print("Error: Invalid date input. ", e)
        return "Error"
    
    

def execute_query_strategy(goal, params):
    """
    Executes a query strategy based on the parameters.

    :param goal: The search goal.
    :param params: Dictionary with the parameters.
    :return: The retrieved data as a pandas dataframe or None if an error occurred.
    """
    strategy = choose_query_strategy(params)
    
    if strategy == "Error":
        return None
    

    if strategy == "condition 3":
        answer = sg.popup_yes_no('You are requesting more than 3 month of data. This operation may take a while due to the large date range, and you need to provide a location to store the data beforehand. Do you want to continue?')
        if answer == "No":
            return None

        dataframe = chunk_query(goal, params)
        return dataframe
    
    
    api_response = get_data(goal, params)
    
    if api_response.status_code == 200:
        data = api_response.json()
        dataframe = convert_to_dataframe(data)
        sg.popup("Data successfully retrieved.")
        return dataframe
    else:
        sg.popup_error("Error retrieving data. Please check your input.")
        return None


def save_data(dataframe):
    """
    Save a dataframe to a file.

    :param dataframe: The dataframe to save.
    """
    if dataframe is not None:
        file_name = sg.popup_get_file("Save data to a file", save_as=True, default_extension=".csv")
        if file_name:
            save_to_file(dataframe, file_name)
            sg.popup("Data successfully saved.")
    else:
        sg.popup_error("No data available to save. Please *Get Data* first.")


def divide_into_chunks(bdate, edate):
    """
    Divide the date range into quarter-year chunks, within the same year for bdate and edate.

    :param bdate: The begin date as a datetime object.
    :param edate: The end date as a datetime object.
    :return: A list of tuples (bdate, edate) for each chunk.
    """
    chunks = []
    while bdate < edate:
        if bdate.month in [1, 2, 3]:  # First quarter
            next_bdate = datetime(bdate.year, 4, 1)
        elif bdate.month in [4, 5, 6]:  # Second quarter
            next_bdate = datetime(bdate.year, 7, 1)
        elif bdate.month in [7, 8, 9]:  # Third quarter
            next_bdate = datetime(bdate.year, 10, 1)
        else:  # Fourth quarter
            next_bdate = datetime(bdate.year + 1, 1, 1)

        if next_bdate > edate:  # If the next bdate exceeds the edate
            next_bdate = edate

        chunks.append((bdate, next_bdate - timedelta(days=1)))  # Subtract one day because the period is inclusive

        bdate = next_bdate

    return chunks

## key query function
def chunk_query(goal, params):
    """
    Query the API in chunks. 
    Handle the case into chunk and store directly when request range exceeds 3 months.
    Ohterwise, store the data into a dataframe and return it.

    :param goal: The search goal.
    :param params: Dictionary with the parameters.
    :return: The retrieved data as a pandas dataframe; or return nothing but create a large .csv file when data range is large.
    """

    bdate = datetime.strptime(params['bdate'], '%Y%m%d')
    edate = datetime.strptime(params['edate'], '%Y%m%d')
    chunks = divide_into_chunks(bdate, edate)

    dataframe = None

    # Define a threshold for number of rows
    # when exceeded, write the dataframe to disk and clear it
    THRESHOLD = 10000
    # user can choose where to save the file and give it a name
    file_name = sg.popup_get_file("Create a file", save_as=True, default_extension=".csv")

    for chunk_bdate, chunk_edate in chunks:
        chunk_params = params.copy()
        chunk_params['bdate'] = chunk_bdate.strftime('%Y%m%d')
        chunk_params['edate'] = chunk_edate.strftime('%Y%m%d')
        
        print('Now requesting: ', goal)
        print('Between datetime: ', chunk_params['bdate'], chunk_params['edate'])
        

        api_response = get_data(goal, chunk_params)
        if api_response.status_code == 200:
            data = api_response.json()
            chunk_dataframe = convert_to_dataframe(data)


            if dataframe is None:
                dataframe = chunk_dataframe
            else:
                dataframe = pd.concat([dataframe, chunk_dataframe], ignore_index=True)

            # When dataframe size reaches THRESHOLD, write it to disk
            if len(dataframe) >= THRESHOLD:
                # Write the dataframe to a CSV file
                # If the file doesn't exist, create it and write with header
                # If the file exists, append to it without writing the header
                with open(file_name, 'a') as f:
                    dataframe.to_csv(f, header=f.tell()==0, index=False)
                    
                # Clear the dataframe
                dataframe = pd.DataFrame()
                

            # if dataframe is None:
            #     dataframe = chunk_dataframe
            # else:
            #     dataframe = pd.concat([dataframe, chunk_dataframe], ignore_index=True)
            print("resting...")
            time.sleep(5)
        else:
            try:
                error_data = api_response.json()
                error_message = error_data.get('message', api_response.text)
            except ValueError:
                error_message = api_response.text
            sg.popup_error(f"Error retrieving data. Message: {error_message}")
            if dataframe is None:
                return None
            else:
                return dataframe
        

    sg.popup("Data successfully retrieved.")
    return dataframe


