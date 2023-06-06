import PySimpleGUI as sg
import database_utils as db

# Function to prompt user to select SQLite database
def select_database():
    layout = [[sg.Text('Choose a SQLite database')],
              [sg.Input(), sg.FileBrowse(file_types=(('SQLite Database', '*.sqlite'),))],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window('Select SQLite database', layout)
    event, values = window.read()
    window.close()
    return values[0]

# Main function
def main():
    # Prompt user to select SQLite database
    sql_database = select_database()
    if sql_database == "":
        sg.PopupError('No database selected. Exiting.')
        return

    # Get table names
    table_names = db.get_all_tables(sql_database)
    if not table_names:
        sg.PopupError('No tables in database. Exiting.')
        return

    # Prompt user to select a table
    layout = [[sg.Text('Choose a table')],
              [sg.Combo(table_names, key='table_name')],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window('Select table', layout)
    event, values = window.read()
    window.close()
    if values['table_name'] == '':
        sg.PopupError('No table selected. Exiting.')
        return
    table_name = values['table_name']

    # Get column names
    column_names = db.get_column_names(table_name,sql_database)
    if not column_names:
        sg.PopupError('No columns in table. Exiting.')
        return

    # Prompt user to select columns, start date, end date, and FIPS code
    layout = [[sg.Text('Choose columns')],
              [sg.Listbox(column_names, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='columns', size= (30, 10))],
              [sg.Text('Start Date'), sg.Input(key='start_date')],
              [sg.Text('End Date'), sg.Input(key='end_date')],
              [sg.Text('FIPS code'), sg.Input(key='fips')],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window('Select columns', layout)
    event, values = window.read()
    window.close()
    if not values['columns']:
        sg.PopupError('No columns selected. Exiting.')
        return
    columns = values['columns']
    start_date = values['start_date']
    end_date = values['end_date']
    fips = values['fips']

    # Query table
    df = db.query_table(sql_database, table_name, columns, start_date, end_date, fips)
    if df.empty:
        sg.PopupError('No data retrieved. Exiting.')
        return

    # Prompt user to choose a location to save CSV
    layout = [[sg.Text('Choose a location to save CSV')],
              [sg.Input(), sg.FolderBrowse()],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window('Select CSV save location', layout)
    event, values = window.read()
    window.close()
    if values[0] == '':
        sg.PopupError('No save location chosen. Exiting.')
        return
    save_location = values[0]

    # Save DataFrame to CSV
    df.to_csv(f'{save_location}/air_quality_data.csv', index=False)
    sg.Popup('CSV file successfully saved.')

# Run the main function
if __name__ == '__main__':
    main()
