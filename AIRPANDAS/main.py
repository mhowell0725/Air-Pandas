from gui import AqsGUI, CensusGUI, dbGUI
import PySimpleGUI as sg

def main():
    '''
    Show case the GUI:
    - Choose from 3 different options: air quality request, census request, or database query
    '''

    # All the stuff inside your window.
    layout = [  [sg.Text('Welcome to AirPandas!')],
                [sg.Text('Please choose from the following options:')],
                [sg.Button('Air Quality Request'), sg.Button('Census Request'), sg.Button('Database Query')] ] 

    # Create the Window
    window = sg.Window('AirPandas', layout)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED:
            break
        elif event == 'Air Quality Request':
            gui = AqsGUI()
            gui.start()
        elif event == 'Census Request':
            gui = CensusGUI()
            gui.start()
        elif event == 'Database Query':
            gui = dbGUI()
            gui.start()
    
    window.close()

if __name__ == '__main__':
    main()