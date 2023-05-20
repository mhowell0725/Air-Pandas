import PySimpleGUI as sg
import aqs_api
import data_processing
import query_utils

def create_param_inputs(goal):
    """
    Create a list of layout elements for the required parameters of the given goal.

    :param goal: The selected goal from the drop-down menu.
    :return: A list of layout elements.
    """
    param_inputs = []
    params = aqs_api.get_params(goal)

    for param in params:
        param_inputs.append(sg.Text(param + ":"))
        param_inputs.append(sg.Input(key=param))

    return param_inputs

# Define the layout for the GUI
layout = [
    [sg.Text("Select a search goal:")],
    [sg.InputCombo(list(aqs_api.load_serach_goals().keys()), key="goal")],
    [sg.Button("Get Data"), sg.Button("Save Data"), sg.Button("Exit")]
]

dataframe = None ## when "get_data", dataframe will be change to that and can be saved

# Create the window with the defined layout
window = sg.Window("EPA AQS Data Retrieval", layout)


# Event loop for handling user interactions
while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, "Exit"):
        break
    elif event == "Get Data":
        goal = values["goal"]
        print(f"Goal: {goal}")  # Debugging: Print the selected goal
        if goal:
            try:
                # Create input fields for the required parameters
                param_inputs = create_param_inputs(goal)
                layout_params = [
                    [sg.Text("Enter the required parameters:")],
                    *[[element] for element in param_inputs],
                    [sg.Button("Submit Parameters"), sg.Button("Cancel")]
                ]
                window_params = sg.Window("Enter Parameters", layout_params)
                
                # Event loop for the parameters window
                while True:
                    event_params, values_params = window_params.read()
                    if event_params in (sg.WIN_CLOSED, "Cancel"):
                        break
                    elif event_params == "Submit Parameters":
                        # Update the complete_params function to accept a dictionary of parameters
                        params = aqs_api.complete_params(aqs_api.get_params(goal), values_params)
                        dataframe = query_utils.execute_query_strategy(goal, params)

                        # print(f"Parameters: {params}")  # Debugging: Print the parameters
                        # print(params.get("bdate"))
                        # print(f"values_params: {values_params}")
                        #  print(f"API Response: {api_response.text}")  # Debugging: Print the API response


                        # api_response = aqs_api.get_data(goal, params)
                        
                        # if api_response.status_code == 200:
                        #     data = api_response.json()
                        #     dataframe = data_processing.convert_to_dataframe(data)
                        #     sg.popup("Data successfully retrieved.")
                        # else:
                        #     sg.popup_error("Error retrieving data. Please check your input.")
                        # break

                window_params.close()
                
            except Exception as e:
                sg.popup_error(f"Error: {str(e)}")


    elif event == "Save Data": ## need to get data first

        query_utils.save_data(dataframe)
        # if dataframe is not None:
        #     file_name = sg.popup_get_file("Save data to a file", save_as=True, default_extension=".csv")
        #     if file_name:
        #         data_processing.save_to_file(dataframe, file_name)
        #         sg.popup("Data successfully saved.")
        # else:
        #     sg.popup_error("No data available to save. Please *Get Data* first.")

window.close()