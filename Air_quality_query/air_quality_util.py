import requests
import json
import pandas as pd

def get_api_key(file_name="myEmailKey.txt"):
    '''
    obtain the email and api key from a file
    require the first line to be email and second line to be api key]

    :param file_name: the file name of the file containing email and api key
    :return: email and api key in a tuple
    '''
    with open(file_name, "r") as file:
        email = file.readline().strip()
        api_key = file.readline().strip()

    return email, api_key

base_url = "https://aqs.epa.gov/data/api"

def create_endpoint(goal):
    '''
    base on user input, find the endpoint where the data is located
    
    '''
    ## key refers to the data, and the value refers to the endpoint we want to pass

    ## need more endpoints

    filters = {
        "States" : "list/states",
        "Counties" : "list/countiesByState",
        "Sites" : "list/sitesByCounty",
        "Parameter Classes" : "list/classes",
        "Parameters" : "list/parametersByClass",
        "Quarterly by County" : "quarterlyData/byCounty",
    }
    
    return filters[goal]

def param_requirement(email, api_key, goal):
    '''
    base on user input, find the required parameters
    '''
    filters = {
    "States" : [],
    "Counties" : ["state"],
    "Sites" : ["state", "county"],
    "Parameter Classes" : [],
    "Parameters" : ["pc"],
    "Quarterly by County" : ["param", "bdate", "edate", "state", "county"]
    }

    ## prompt user to enter the required parameters
    required_params = filters[goal]
    params = {
        "email": email,
        "key": api_key,
    }
    ## ask user to type in extra parameters in the terminal
    for i in required_params:
        params[i] = input("Please enter {}: ".format(i))

    return params

def get_data(endpoint, params):
    '''
    get the data from the api, return as pandas dataframe
    '''
    response = requests.get(base_url + "/" + endpoint, params=params)

    ## check if the request is successful
    if response.status_code != 200:
        raise Exception("Request failed with status code {}".format(response.status_code))

    ## convert the response to json and then to pandas dataframe
    data = response.json()
    df = pd.DataFrame.from_dict(data["Data"])

    return df








