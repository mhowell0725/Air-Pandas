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

base_url = "https://aqs.epa.gov/data/api/"

def get_endpoint(goal):
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
        "Daily by State" : "dailyData/byState"
    }
    
    try:
        return filters[goal]
    except KeyError:
        raise ValueError("Invalid goal entered. Please make sure you're entering a valid option from the filters list.")

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
    "Quarterly by County" : ["param", "bdate", "edate", "state", "county"],
    "Daily by State" : ["param", "bdate", "edate", "state"]
    }

    ## prompt user to enter the required parameters
    try:
        required_params = filters[goal]
    except KeyError:
        raise ValueError("Invalid goal entered. Please make sure you're entering a valid option from the filters list.")
    
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
    response = requests.get(base_url + endpoint, params=params)

    ## check if the request is successful
    if response.status_code != 200:
        try:
            error_message = response.json()["Message"]
        except KeyError:
            error_message = "Unknown error"
        raise Exception(f"Request failed with status code {response.status_code}. Error: {error_message}")

    ## convert the response to json and then to pandas dataframe
    data = response.json()

    if "Data" not in data:
        raise ValueError("No data found in the API response. Please check the input parameters and try again.")
   
    df = pd.DataFrame.from_dict(data["Data"])

    return df

# main function
def main():
    email, api_key = get_api_key()
    print("Please choose a data retrieval goal from the following list:")
    
    filters = {
        "States" : "list/states",
        "Counties" : "list/countiesByState",
        "Sites" : "list/sitesByCounty",
        "Parameter Classes" : "list/classes",
        "Parameters" : "list/parametersByClass",
        "Quarterly by County" : "quarterlyData/byCounty",
        "Daily by State" : "dailyData/byState"
    }
    
    for key in filters:
        print(key)
    
    goal = input("Enter the desired goal: ")

    try:
        endpoint = get_endpoint(goal)
        required_params = param_requirement(email, api_key, goal)
    except ValueError as e:
        print(e)
        return

    try:
        df = get_data(endpoint, required_params)
        print(df)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()








