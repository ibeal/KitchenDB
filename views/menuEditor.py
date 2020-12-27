import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
# import KitchenGUI.searchBar as searchBar
from DB.database import *
from recipeCreator import *
from apiCalls import *
from KitchenModel import *
from views.view import view
from controllers.menuEditorController import *
logger = logging.getLogger('menuEditor Log')

class menuEditor(sg.Tab, view):
    def __init__(self, title, master, *args, **kwargs):
        self.model = KitchenModel.getInstance()
        self.master = master
        self.recFields = {field: f'-{field}-BOX-' for field in recipe.pretty_fields}
        super().__init__(title, layout=self.layout_init(), *args, **kwargs)

        self.model.addTab("-MENU-", self, menuEditorController(),
            {})

    def refreshView(self, model, key):
        pass

    def layout_init(self):
        layout = [
                [sg.T('Menu'),
                 sg.In('12/03/21-12/17/21'),
                 sg.Button('Select Menu'),
                 sg.Button('Shopping List'),
                 sg.Button('Add Recipe')],
                [sg.T('Menu for: '),
                 sg.Combo(values=['12/03/21'], default_value='12/03/21')],
                [sg.T('Breakfast')],
                [sg.Multiline(size=(50,8))],
                [sg.T('Lunch')],
                [sg.Multiline(size=(50,8))],
                [sg.T('Dinner')],
                [sg.Multiline(size=(50,8))],
                [sg.T('Misc.')],
                [sg.Multiline(size=(50,8))],
        ]
        return layout
