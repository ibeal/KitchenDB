import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from DB.database import *
from recipeCreator import *
from apiCalls import *
from KitchenModel import *
from controllers.controller import controller
import KitchenGUI.searchBar as searchBar
import menu as Menu
import numpy as np
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
            if self.model.get('activeMenu') == None or self.model.get('activeMenuDay') == None:
                sg.PopupError('No Menu Selected!', title='Error')
                return True
            self.add_recipe()
            return True
        elif event == "-MENU-DAY-":
            self.model.set('activeMenuDay', value=self.model.get('activeMenu').getDay(values['-MENU-DAY-']))
            return True
        elif event == "-MENU-SAVE-":
            self.model.get('MenuAPI').saveMenu(self.model.get('activeMenu'))
            return True
        return False

    def save_menu(self):
        pass

    def add_recipe(self):
        search = searchBar.searchBar(key='-MODAL-SEARCH-', api=self.model.get('RecipeAPI'), length=40, searchbutton=False, getID=True)
        layout = [
            [search],
            [sg.T('Add To: '),
             sg.T(self.model.get('activeMenuDay').date),
             sg.T('Menu: '),
             sg.T(self.model.get('activeMenu').getName())],
            [sg.T('Recipe Mulitiplier: '),
             sg.Combo(values=[f'{i}' for i in np.arange(.5,5,.5)], key='-MODAL-MULTBY-',
                     default_value='1')],
            [sg.T('Under Section: '),
             sg.Combo(values=list(self.model.get('activeMenuDay').data.keys()), key='-MODAL-GROUP-')],
            [sg.Button('Add', key="-MODAL-ADD-"),
             sg.Button('Cancel', key="-MODAL-CANCEL-")]
        ]

        window = sg.Window('Select Menu', layout, finalize=True)
        # load active recipe into search bar

        while True:
            event, values = window.read()

            if search.handle(event, values):
                continue
            if event in (sg.WIN_CLOSED, "-MODAL-CANCEL-"):
                break

            elif event == "-MODAL-ADD-":
                rec = self.model.get('RecipeAPI').recipeLookup(recID=values[search.sbox_key])
                date = self.model.get('activeMenuDay').date
                group = values['-MODAL-GROUP-']
                mult = values['-MODAL-MULTBY-']
                self.model.get('activeMenu').addRecipe(rec=rec*mult, date=date, group=group)
                self.model.notifyOberservers('activeMenuDay')
                break

        window.close()

    def select_menu_modal(self):
        search = searchBar.searchBar(key='-MODAL-SEARCH-', api=self.model.get('MenuAPI'), length=20, searchbutton=False)
        layout = [
            [search],
            [sg.Button('Open', key="-MODAL-OPEN-"),
             sg.Button('Add New', key="-MODAL-NEW-"),
             sg.Button('Cancel', key="-MODAL-CANCEL-")]
        ]

        window = sg.Window('Select Menu', layout, finalize=True)
        new = False

        while True:
            event, values = window.read()

            if search.handle(event, values):
                continue
            if event in (sg.WIN_CLOSED, "-MODAL-CANCEL-"):
                break
            elif event == "-MODAL-NEW-":
                new = True
                break
            elif event == "-MODAL-OPEN-":
                menu = values[search.sbox_key]
                menu = self.model.get('MenuAPI').menuLookup(menu)
                self.model.set('activeMenu', value=menu)
                self.model.set('activeMenuDay', value=menu.getDay(0))
                break

        window.close()

        if new:
            self.new_menu_modal()

    def new_menu_modal(self):
        calendar_icon = './KitchenGUI/calendar2.png'
        layout = [
            [sg.T('Date Range: '),
             sg.In(key='-MODAL-START-', enable_events=True, size=(10,1)),
             sg.CalendarButton('', format='%Y-%m-%d',
             button_color=(sg.theme_background_color(), sg.theme_background_color()),
             image_filename=calendar_icon, image_subsample=8),
             sg.T('To'),
             sg.In(key='-MODAL-END-', enable_events=True, size=(10,1)),
             sg.CalendarButton('', format='%Y-%m-%d',
             button_color=(sg.theme_background_color(), sg.theme_background_color()),
             image_filename=calendar_icon, image_subsample=8)],
            [sg.T('Menu Name: '),
             sg.In(key='-MODAL-NAME-', enable_events=True, size=(36,1))],
            [sg.Button('Create', key="-MODAL-CREATE-"),
             sg.Button('Cancel', key="-MODAL-CANCEL-")]
        ]

        window = sg.Window('New Menu', layout, finalize=True)
        set_name = False
        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "-MODAL-CANCEL-"):
                break
            elif event == "-MODAL-NAME-":
                set_name = True
            elif event == "-MODAL-CREATE-":
                start = window['-MODAL-START-'].get()
                end = window['-MODAL-END-'].get()
                name = window['-MODAL-NAME-'].get()
                new_menu = Menu.menu(start=start, end=end, name=name)
                self.model.set('activeMenu', value=new_menu)
                break
            if not set_name:
                start = window['-MODAL-START-'].get()
                end = window['-MODAL-END-'].get()
                window['-MODAL-NAME-'].update(value=f'{start}{Menu.menu.date_delimiter}{end}')

        window.close()
