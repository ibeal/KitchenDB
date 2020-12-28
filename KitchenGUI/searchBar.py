import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg

def searchBar(master, key='', length=40, *args, **kwargs):
    sbox = sg.In(key=f'-{key}-SBOX-', size=(length,1),*args, **kwargs)
    # master.expands['x'].append(sbox)
    sbutton = sg.Button('Search',key=f'-{key}-SBUTTON-')
    opt = [['test'], ['test']]
    layout = [
                [sg.T('Search'), sbox, sbutton],
                [sg.Table(headings=None, values=opt, num_rows=3,
                enable_events=True, auto_size_columns=False, col_widths=[length]) ]
             ]
    return sg.Column(layout=layout)
