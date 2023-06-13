import PySimpleGUI as sg
import aqs_request
import census_request
import database_query as dbq
import visualization as viz
import textwrap

class AqsGUI:
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

class CensusGUI:
    def __init__(self):
        self.api_key = census_request.get_api_key()
        self.category_code_dict = census_request.read_json('AIRPANDAS\json\category_code.json')
        self.year_category_abbrev_dict = census_request.read_json('AIRPANDAS\json\year_category_abbrev.json')
        self.categories = set()

        for year in self.year_category_abbrev_dict:
            self.categories.update(self.year_category_abbrev_dict[year].keys())

        self.layout = [
            [sg.Text("Select a category:")],
            [sg.InputCombo(list(self.categories), key="category")],
            [sg.Text("Select a year:")],
            [sg.InputCombo(list(range(2009, 2022)), key="year")],
            [sg.Button("Get Data"), sg.Button("Exit")]
        ]
        
        self.window = sg.Window("US Census Data Retrieval", self.layout)

    def start(self):
        while True:
            event, values = self.window.read()

            if event in (sg.WIN_CLOSED, "Exit"):
                break
            elif event == "Get Data":
                category = values["category"]
                year = values["year"]
                
                if category and year:
                    try:
                        census_request.query_census_data(int(year), int(year), category)
                        sg.popup('Data successfully retrieved and saved as CSV')
                    except Exception as e:
                        sg.popup_error(f"Error: {str(e)}")

        self.window.close()




class dbGUI:
    def __init__(self):
        self.database = None

    def start(self):
        if self.database == None:
            self.database = self.select_database()
            if self.database == None:
                return
        self.main_menu()
                
    def select_database(self):
        layout = [
            [sg.Text('Choose a SQLite database')],
            [sg.Input(), sg.FileBrowse(file_types=(('SQLite Database', '*.sqlite'),))],
            [sg.OK(), sg.Cancel()]
        ]

        window = sg.Window('Select SQLite database', layout)

        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, 'Cancel'):
                break
            elif event == 'OK':
                if values[0]:  # if a file has been selected
                    window.close()
                    return values[0]

        window.close()
        return None

    def main_menu(self):
        layout = [
            [sg.Text('Choose an operation')],
            [sg.Button('Query data from a table')],
            [sg.Button('Plotting')],
            [sg.Button('Exit')]
        ]

        window = sg.Window('Main Menu', layout)

        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                break
            elif event == 'Query data from a table':
                self.query_data()
            elif event == 'Plotting':
                window.close()
                self.visualization()

        window.close()

    def query_data(self):
        tables = dbq.get_all_tables(self.database)
        table_layout = [
            [sg.Text('Choose a table')],
            [sg.Listbox(values=tables, size=(30, len(tables)), key='-TABLE-', enable_events=True)],
            [sg.Button('OK'), sg.Button('Back')]
        ]

        table_window = sg.Window('Select Table', table_layout)

        while True:
            event, values = table_window.read()
            if event in (sg.WINDOW_CLOSED, 'Back'):
                break
            elif event == 'OK':
                table_name = values['-TABLE-'][0]
                columns = dbq.get_column_names(table_name, self.database)
                column_layout = [
                    [sg.Text('Choose columns')],
                    [sg.Listbox(values=columns, size=(30, len(columns)), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='-COLUMNS-')],
                    [sg.Button('OK'), sg.Button('Back')]
                ]

                column_window = sg.Window('Select Columns', column_layout)

                while True:
                    event, values = column_window.read()
                    if event in (sg.WINDOW_CLOSED, 'Back'):
                        break
                    elif event == 'OK':
                        selected_columns = values['-COLUMNS-']
                        date_layout = [
                            ## add a helper note to explain date format
                            [sg.Text('Enter dates in YYYY-MM-DD format for Airquality data, YYYY for Census data')],
                            [sg.Text('Enter start date'), sg.InputText(key='-START_DATE-')],
                            [sg.Text('Enter end date'), sg.InputText(key='-END_DATE-')],
                            [sg.Text('Enter FIPS code (optional)'), sg.InputText(key='-FIPS-')],
                            [sg.Button('Submit'), sg.Button('Back')]
                        ]

                        date_window = sg.Window('Enter Dates and FIPS Code', date_layout)
                        while True:
                            event, values = date_window.read()
                            if event in (sg.WINDOW_CLOSED, 'Back'):
                                break
                            elif event == 'Submit':
                                sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
                                
                                start_date = values['-START_DATE-']
                                end_date = values['-END_DATE-']
                                fips = values['-FIPS-'] if values['-FIPS-'] else None
                                df = dbq.query_table(self.database, table_name, selected_columns, start_date, end_date, fips)
                                
                                sg.popup_animated(None)

                                print("dataframe:",df.head())
                                df.to_csv(f'{table_name}_{start_date}_{end_date}.csv')
                                sg.popup(f'Data successfully retrieved and saved as {table_name}_{start_date}_{end_date}.csv')
                                
                        date_window.close()

                column_window.close()
        table_window.close()

    def visualization(self):
        tables = dbq.get_all_tables(self.database)
        table_layout = [
            [sg.Text('Choose a *Census* table')],
            [sg.Listbox(values=tables, size=(30, len(tables)), key='-TABLE-', enable_events=True)],
            [sg.Button('OK'), sg.Button('Back')]
        ]

        table_window = sg.Window('Select Table', table_layout)

        while True:
            event, values = table_window.read()
            if event in (sg.WINDOW_CLOSED, 'Back'):
                break
            elif event == 'OK':
                table_name = values['-TABLE-'][0]
                columns = dbq.get_column_names(table_name, self.database)
                column_layout = [
                    [sg.Text('Choose columns')],
                    [sg.Listbox(values=columns, size=(30, len(columns)), key='-COLUMNS-')],
                    [sg.Button('OK'), sg.Button('Back')]
                ]

                column_window = sg.Window('Select Columns', column_layout)

                while True:
                    event, values = column_window.read()
                    if event in (sg.WINDOW_CLOSED, 'Back'):
                        break
                    elif event == 'OK':
                        selected_columns = values['-COLUMNS-']
                        year_threshold_layout = [
                            [sg.Text('Choose a Year (2009 - 2021) and a Threshold for PM2.5')],
                            [sg.Spin([i for i in range(2009, 2022)], initial_value=2009, key='-YEAR-', size=(10, 1))],
                            [sg.Text('Enter threshold for PM2.5, the plot will show the percentage of time above this threshold')],                            
                            [sg.Input(key='-THRESHOLD-', size=(10, 1)),sg.Text('ug/m^3')],
                            [sg.Text('Note: below 12 ug/m^3 is healthy, 25 is fair, 50 is poor, 100+ is very poor')],
                            [sg.Button('OK'), sg.Button('Back')]
                        ]

                        year_threshold_window = sg.Window('Select Year and Threshold', year_threshold_layout)

                        while True:
                            event, values = year_threshold_window.read()
                            if event in (sg.WINDOW_CLOSED, 'Back'):
                                break
                            elif event == 'OK':
                                # show loading gif
                                sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
                                year = int(values['-YEAR-'])
                                threshold = float(values['-THRESHOLD-'])

                                # create the plot
                                fig, _ = viz.create_side_comparison(threshold, year, table_name, selected_columns)
                                fig.write_html(f"{table_name}_comparison_{year}.html")

                                # stop loading gif
                                sg.popup_animated(None)

                        year_threshold_window.close()

                column_window.close()

        table_window.close()
