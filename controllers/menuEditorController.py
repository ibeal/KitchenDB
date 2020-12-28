import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from DB.database import *
from recipeCreator import *
from apiCalls import *
from KitchenModel import *
from controllers.controller import controller
logger = logging.getLogger('menuEditorController Log')

class menuEditorController(controller):
    def __init__(self):
        self.model = KitchenModel.getInstance()

    def setup(self):
        pass

    def handle(self, event, values):
        if event == "-MENU-SELECT-":
            self.select_menu_modal()
            return True
        elif event == "-MENU-SHOPPING-":
            return True
        elif event == "-MENU-ADD-RECIPE-":
            return True
        return False

    def select_menu_modal(self):
        layout = [
            [sg.T('Name: '),
             sg.Combo(values=[], default_value='', key="-MODAL-SEARCH-", enable_events=True, size=(20,1))],
            [sg.Button('Open', key="-MODAL-OPEN-"),
             sg.Button('Add New', key="-MODAL-NEW-"),
             sg.Button('Cancel', key="-MODAL-CANCEL-")]
        ]

        window = sg.Window('Select Menu', layout, finalize=True)
        new = False

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "-MODAL-CANCEL-"):
                break
            elif event == "-MODAL-NEW-":
                new = True
                break
            elif event == "-MODAL-OPEN-":
                menu = values["-MODAL-SEARCH-"]
                menu = self.model.get('MenuAPI').menuLookup(menu)
                self.model.set('activeMenu', menu)
                break
            elif event == "-MODAL-SEARCH-":
                # # TODO: add search feature
                menu = values["-MODAL-SEARCH-"]
                options = self.model.get('MenuAPI').search(menu)
                window["-MODAL-SEARCH-"].update(values=options)

        window.close()

        if new:
            self.new_menu_modal()

    def new_menu_modal(self):
        pass
