import PySimpleGUI as sg
# Based on https://www.pysimplegui.org/en/latest/cookbook/#recipe-pattern-2a-persistent-window-multiple-reads-using-an-event-loop



#Set a color scheme for the window
# https://www.pysimplegui.org/en/latest/cookbook/#themes-window-beautification
sg.theme('DarkAmber')

"""
Set the layout of your window
Your window will be arranged in a grid of elements, where each element will
show a different kind of information or allow a different kind of input.
When we actually create the window that will be shown, we pass this layout in
to tell it what to look like.

For an overview of elements, see
https://www.pysimplegui.org/en/latest/cookbook/#recipe-all-elements-the-everything-bagel-2022-style
"""

layout = [  [sg.Text('Some text on Row 1')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.Button('Add one'), sg.Text(0, key="-COUNTER-")],
            [sg.Button('Ok'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Window Title', layout)
# Event Loop to process "events" and get the "values" of the inputs

"""
To be able to interact with the window, we need to put it inside a for loop
so it stays on our screen. Every time the loop runs, the window.read()
will check for changes in the window (such as input being added, a button
being pressed, etc.). By reading in the events and the values, we can figure
out what input was made and act accordingly.
"""

output = ""
while True:
    # Read in any events and the current state of the window
    event, values = window.read()
    # If we eclosed the window or clicked the Cancel button, break out of the
    # loop
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    
    # If user presses "add one"
    if event == "Add one":
        # Update the counter text with the current text + 1
        window['-COUNTER-'].update(int(window['-COUNTER-'].get()) + 1)
    
    # If user presses "Ok"
    if event == "Ok":
        # Save the current value of the counter and close the window
        output = window['-COUNTER-'].get()
        break


window.close()
print(f"Output: {values[0]}{output}")
