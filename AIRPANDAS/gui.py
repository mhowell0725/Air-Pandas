import PySimpleGUI as sg
import aqs_request
import textwrap

class AqsGui:
    def __init__(self):

        # Define the layout for the GUI
        self.layout = [
            [sg.Text("Select a search goal:")],
            [sg.InputCombo(list(aqs_request.load_serach_goals().keys()), key="goal")],
            [sg.Button("Get Data"), 
             sg.Button("Save Data", disabled=True, key="Save Data"), ## not shown until data is retrieved
             sg.Button("Show Data", disabled=True, key="Show Data"), 
             sg.Button("Exit")]
        ]


        ## load param descriptions and wrap them so that they show up nicely in the GUI
        self.param_descriptions = aqs_request.load_param_descriptions()
        for param, description in self.param_descriptions.items():
            self.param_descriptions[param] = textwrap.fill(description, width=50)
        self.dataframe = None

        # Create the window with the defined layout
        self.window = sg.Window("EPA AQS Data Retrieval", self.layout)

    def _create_aqs_param_inputs(self, goal):
        """
        Create a list of layout elements for the required parameters of the given goal.
        Would be called each time for each param in the goal

        :param goal: The selected goal from the drop-down menu.
        :return: A list of layout elements. --- Show up in GUI as one line in the param input window
        """
        aqs_param_inputs = []
        params = aqs_request.get_params(goal)

        for param in params:
            param_description = self.param_descriptions.get(param, "No description available.")
            aqs_param_inputs.append([sg.Text(param + ":"), 
                                 sg.Input(key=param),
                                 sg.pin(sg.Button('?', 
                                                  # when hover show both param and description
                                                  tooltip= f'{param}: {param_description}',
                                                  button_color=('black', 'white'), 
                                                  border_width=0,
                                                  key=f'Help_{param}'))])
        
        return aqs_param_inputs

    def _handle_help(self, param):
        """
        Display a window with the description of the given parameter.
        Define the behavior for "?" button in the param input window 
        hover && click, show what's in the param_descriptions (json)

        :param param: The parameter to display the description for.
        """

        description = self.param_descriptions.get(param, "No description available.")
        layout_description = [
            [sg.Text(f"{param}:\n{description}")],
            [sg.Button("Close")]
        ]
        window_description = sg.Window("Parameter Description", layout_description)

        while True:
            event_description, _ = window_description.read()
            if event_description in (sg.WIN_CLOSED, "Close"):
                break

        window_description.close()

    def start(self):
        """
        Main loop of the AQS request GUI.
        Call this method to start the GUI.
        
        """
        while True:
            event, values = self.window.read()

            if event in (sg.WIN_CLOSED, "Exit"):
                break
            elif event == "Get Data":
                goal = values["goal"]
                #print(f"Goal: {goal}")  # For Debugging: Print the selected goal
                if goal:
                    try:
                        # Create input fields for the required parameters
                        aqs_param_inputs = self._create_aqs_param_inputs(goal)
                        layout_params = [
                            [sg.Text("Enter the required parameters:")],
                            ## reflect every singe param in the goal
                            *[[element] for element in aqs_param_inputs],
                            [sg.Button("Submit Parameters"), sg.Button("Cancel")]
                        ]
                        window_params = sg.Window("Enter Parameters", layout_params)
                        
                        while True:
                            event_params, values_params = window_params.read()
                            if event_params in (sg.WIN_CLOSED, "Cancel"):
                                break
                            elif event_params == "Submit Parameters":
                                params = aqs_request.complete_params(aqs_request.get_params(goal), values_params)
                                self.dataframe = aqs_request.execute_query_strategy(goal, params)
                                ## allow user to save and show data when data is retrieved
                                self.window['Save Data'].update(disabled=False)
                                self.window['Show Data'].update(disabled=False)                                  
                            elif event_params.startswith("Help_"):
                                param = event_params.split("_")[1]
                                self._handle_help(param)
                        
                        window_params.close()
                 
                        
                    except Exception as e:
                        sg.popup_error(f"Error: {str(e)}")
            elif event == "Save Data":
                # Save the dataframe to a CSV file
                aqs_request.save_data(self.dataframe)
            elif event == "Show Data":
                # Show a few lines of the dataframe in a popup table
                sg.popup_scrolled(self.dataframe.head(), title="Data Preview (5 Rows)")

        self.window.close()

# Using the GUI
gui = AqsGui()
gui.start()



# import PySimpleGUI as sg
# import aqs_request
# import textwrap


# param_descriptions = aqs_request.load_param_descriptions()
# for param, description in param_descriptions.items():
#     param_descriptions[param] = textwrap.fill(description, width=50)


# def create_aqs_param_inputs(goal):
#     """
#     Create a list of layout elements for the required parameters of the given goal.

#     :param goal: The selected goal from the drop-down menu.
#     :return: A list of layout elements.
#     """
#     aqs_param_inputs = []
#     params = aqs_request.get_params(goal)


#     for param in params:
#         param_description = param_descriptions.get(param, "No description available.")
#         aqs_param_inputs.append([sg.Text(param + ":"), 
#                              sg.Input(key=param),
#                              sg.pin(sg.Button('?', 
#                                               # when hover show both param and description
#                                               tooltip= f'{param}: {param_description}',
#                                               button_color=('black', 'white'), 
#                                               border_width=0,
#                                               key=f'Help_{param}'))])
    

#     return aqs_param_inputs

# # Define the layout for the GUI
# layout = [
#     [sg.Text("Select a search goal:")],
#     [sg.InputCombo(list(aqs_request.load_serach_goals().keys()), key="goal")],
#     [sg.Button("Get Data"), sg.Button("Save Data"), sg.Button("Exit")]
# ]

# dataframe = None ## when "get_data", dataframe will be change to that and can be saved

# # Create the window with the defined layout
# window = sg.Window("EPA AQS Data Retrieval", layout)

# # Event loop for handling user interactions
# while True:
#     event, values = window.read()

#     if event in (sg.WIN_CLOSED, "Exit"):
#         break
#     elif event == "Get Data":
#         goal = values["goal"]
#         #print(f"Goal: {goal}")  # For Debugging: Print the selected goal
#         if goal:
#             try:
#                 # Create input fields for the required parameters
#                 aqs_param_inputs = create_aqs_param_inputs(goal)
#                 layout_params = [
#                     [sg.Text("Enter the required parameters:")],
#                     *[[element] for element in aqs_param_inputs],
#                     [sg.Button("Submit Parameters"), sg.Button("Cancel")]
#                 ]
#                 window_params = sg.Window("Enter Parameters", layout_params)
                
#                 # Event loop for the parameters window
#                 while True:
#                     event_params, values_params = window_params.read()
#                     if event_params in (sg.WIN_CLOSED, "Cancel"):
#                         break
#                     elif event_params == "Submit Parameters":
#                         # Update the complete_params function to accept a dictionary of parameters
#                         params = aqs_request.complete_params(aqs_request.get_params(goal), values_params)
#                         dataframe = aqs_request.execute_query_strategy(goal, params)
                        
#                     elif event_params.startswith("Help_"):
#                         # Get the parameter this help button is associated with
#                         param = event_params.split("_")[1]
#                         # Get the description of this parameter
#                         description = param_descriptions.get(param, "No description available.")
#                         # Create a new window to display the parameter and its description
#                         layout_description = [
#                             [sg.Text(f"{param}:\n{description}")],
#                             [sg.Button("Close")]
#                         ]
#                         window_description = sg.Window("Parameter Description", layout_description)
                        
#                         # Event loop for the description window
#                         while True:
#                             event_description, values_description = window_description.read()
#                             if event_description in (sg.WIN_CLOSED, "Close"):
#                                 break

#                         window_description.close()
                    

#                 window_params.close()
                
#             except Exception as e:
#                 sg.popup_error(f"Error: {str(e)}")


#     elif event == "Save Data": ## need to get data first

#         aqs_request.save_data(dataframe)


# window.close()