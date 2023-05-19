import requests
import json

base_url = "https://aqs.epa.gov/data/api/"

def get_api_key(file_name = "myEmailKey.txt"):
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


def load_serach_goals(file_name = "search_goals.json"):
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
    Complete request pull from EQA API with a give goal
    :param goal: the goal of the request (e.g. "Daily by State")

    return a request object of the data --- to be converted in data_processing

    used function:
    get_endpoint()
    get_params()
    complete_params()
    '''
    endpoint = get_endpoint(goal)
    # params_requirement = get_params(goal)
    # params = complete_params(params_requirement)

    response = requests.get(base_url + endpoint, params = params)

    ## convert the response to json

    # response = response.json()

    # ##
    # if "Data" not in response:
    #     raise ValueError(f"No data found for the given parameters: {params}") 
    
    return response







def main():
    cp = complete_params(get_params("Daily by State"), {"param": "44201", "bdate": "20200101", "edate": "20200131", "state": "06", "county": "073"})
    print(cp)



if __name__ == "__main__":
    main()