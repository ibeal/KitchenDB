import logging
# import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
import PySimpleGUIQt as sg

def searchBar(master,key=''):
    sbox = sg.In('search...',key=f'-{key}-SBOX-')
    master.expands['x'].append(sbox)
    sbutton = sg.Button('Search',key=f'-{key}-SBUTTON-')
    return [sbox, sbutton]
