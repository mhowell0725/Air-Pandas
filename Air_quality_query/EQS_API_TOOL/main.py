import PySimpleGUI as sg
import aqs_api
import data_processing ## not implemented yet
import query_utils
import textwrap


param_descriptions = aqs_api.load_param_descriptions()
for param, description in param_descriptions.items():
    param_descriptions[param] = textwrap.fill(description, width=50)


def create_param_inputs(goal):
    """
    Create a list of layout elements for the required parameters of the given goal.

    :param goal: The selected goal from the drop-down menu.
    :return: A list of layout elements.
    """
    param_inputs = []
    params = aqs_api.get_params(goal)


    for param in params:
    #     param_inputs.append(sg.Text(param + ":"))
    #     param_inputs.append(sg.Input(key=param))
    #     param_inputs.append(sg.Button("Help_" + param)) # a help button for each parameter
        param_description = param_descriptions.get(param, "No description available.")
        param_inputs.append([sg.Text(param + ":"), 
                             sg.Input(key=param),
                             sg.pin(sg.Button('?', 
                                              # when hover show both param and description
                                              tooltip= f'{param}: {param_description}',
                                              button_color=('black', 'white'), 
                                              border_width=0,
                                              key=f'Help_{param}'))])
    

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
        #print(f"Goal: {goal}")  # For Debugging: Print the selected goal
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
                        
                    elif event_params.startswith("Help_"):
                        # Get the parameter this help button is associated with
                        param = event_params.split("_")[1]
                        # Get the description of this parameter
                        description = param_descriptions.get(param, "No description available.")
                        # Create a new window to display the parameter and its description
                        layout_description = [
                            [sg.Text(f"{param}:\n{description}")],
                            [sg.Button("Close")]
                        ]
                        window_description = sg.Window("Parameter Description", layout_description)
                        
                        # Event loop for the description window
                        while True:
                            event_description, values_description = window_description.read()
                            if event_description in (sg.WIN_CLOSED, "Close"):
                                break

                        window_description.close()
                    

                window_params.close()
                
            except Exception as e:
                sg.popup_error(f"Error: {str(e)}")


    elif event == "Save Data": ## need to get data first

        query_utils.save_data(dataframe)


window.close()