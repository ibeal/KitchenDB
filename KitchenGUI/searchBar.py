import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg

def searchBar(master,key='', *args, **kwargs):
    sbox = sg.In(key=f'-{key}-SBOX-',*args, **kwargs)
    master.expands['x'].append(sbox)
    sbutton = sg.Button('Search',key=f'-{key}-SBUTTON-')
    return [sg.T('Search'), sbox, sbutton]
