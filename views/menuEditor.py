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
        if key == 'activeMenu':
            if self.model.get('activeMenu') == None:
                self.clearMenu()
            else:
                self.loadMenu(self.model.get('activeMenu'))
        if key == 'activeMenuDay':
            if self.model.get('activeMenuDay') == None:
                self.clearFields()
            else:
                self.fillFields(self.model.get('activeMenuDay'))

    def layout_init(self):
        layout = [
                [sg.T('Menu'),
                 sg.In('', key="-MENU-NAME-", size=(20,1)),
                 sg.Button('Select Menu', key="-MENU-SELECT-"),
                 sg.Button('Shopping List', key="-MENU-SHOPPING-"),
                 sg.Button('Add Recipe', key="-MENU-ADD-RECIPE-")],
                [sg.T('Menu for: '),
                 sg.Combo(values=[], default_value='', key="-MENU-DAY-", size=(15,1), enable_events=True)],
                [sg.T('Breakfast')],
                [sg.Multiline(size=(50,8), key="-BREAKFAST-")],
                [sg.T('Lunch')],
                [sg.Multiline(size=(50,8), key="-LUNCH-")],
                [sg.T('Dinner')],
                [sg.Multiline(size=(50,8), key="-DINNER-")],
                [sg.T('Misc.')],
                [sg.Multiline(size=(50,8), key="-MISC-")],
        ]
        return layout

    def fillFields(self, day):
        # keys = list(menu.menus.keys())
        # firstDay = menu.getDay(0)
        # self.model.window["-MENU-NAME-"].update(value=menu.name)
        self.model.window["-MENU-DAY-"].update(value=day.date)
        self.model.window["-BREAKFAST-"].update(value='\n'.join(day.get('breakfast')))
        self.model.window["-LUNCH-"].update(value='\n'.join(day.get('lunch')))
        self.model.window["-DINNER-"].update(value='\n'.join(day.get('dinner')))
        self.model.window["-MISC-"].update(value='\n'.join(day.get('misc')))

    def loadMenu(self, menu):
        keys = list(menu.menus.keys())
        firstDay = menu.getDay(0)
        self.model.window["-MENU-NAME-"].update(value=menu.name)
        self.model.window["-MENU-DAY-"].update(values=keys)
        # self.fillFields(firstDay)

    def clearMenu(self):
        self.model.window["-MENU-NAME-"].update(value='')
        self.model.window["-MENU-DAY-"].update(values=[], value='')
        self.model.window["-BREAKFAST-"].update(value='')
        self.model.window["-LUNCH-"].update(value='')
        self.model.window["-DINNER-"].update(value='')
        self.model.window["-MISC-"].update(value='')

    def clearFields(self):
        self.model.window["-BREAKFAST-"].update(value='')
        self.model.window["-LUNCH-"].update(value='')
        self.model.window["-DINNER-"].update(value='')
        self.model.window["-MISC-"].update(value='')
