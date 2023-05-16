import PySimpleGUI as sg
import aqs_api
import data_processing

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
        try:
            api_response = aqs_api.get_data(goal)
            if api_response.status_code == 200:
                data = api_response.json()
                dataframe = data_processing.convert_to_dataframe(data)
                sg.popup("Data successfully retrieved.")
            else:
                sg.popup_error("Error retrieving data. Please check your input.")
        except Exception as e:
            sg.popup_error(f"Error: {str(e)}")

    elif event == "Save Data": ## need to get data first
        if dataframe is not None:
            file_name = sg.popup_get_file("Save data to a file", save_as=True, default_extension=".csv")
            if file_name:
                data_processing.save_to_file(dataframe, file_name)
                sg.popup("Data successfully saved.")
        else:
            sg.popup_error("No data available to save. Please retrieve data first.")

window.close()