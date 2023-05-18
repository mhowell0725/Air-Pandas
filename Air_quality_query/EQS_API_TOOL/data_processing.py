import pandas as pd

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
