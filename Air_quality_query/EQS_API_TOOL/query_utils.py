from datetime import datetime, timedelta

import aqs_api
import data_processing
import PySimpleGUI as sg
import time
import pandas as pd

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
    
    
    api_response = aqs_api.get_data(goal, params)
    
    if api_response.status_code == 200:
        data = api_response.json()
        dataframe = data_processing.convert_to_dataframe(data)
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
            data_processing.save_to_file(dataframe, file_name)
            sg.popup("Data successfully saved.")
    else:
        sg.popup_error("No data available to save. Please *Get Data* first.")




def chunk_query(goal, params):

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
        print(chunk_params)
        print(goal)

        api_response = aqs_api.get_data(goal, chunk_params)
        if api_response.status_code == 200:
            data = api_response.json()
            chunk_dataframe = data_processing.convert_to_dataframe(data)


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
