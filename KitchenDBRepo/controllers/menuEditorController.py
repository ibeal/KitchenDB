import logging, sys
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
# from DB.database import database
# from containers.recipe import recipe
# from apiCalls import apiCalls
from KitchenModel import KitchenModel
from controllers.controller import controller
import KitchenGUI.searchBar as searchBar
import containers.menu as Menu
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
            self.display_missing_recipes()
            return True
        elif event == "-MENU-SHOPPING-":
            self.model.get('activeMenu').newShoppingList()
            self.shopping_modal()
            return True
        elif event == "-MENU-DELETE-":
            if self.model.get('MenuAPI').menuExists(self.model.get('activeMenu')):
                self.model.get('MenuAPI').deleteMenu(self.model.get('activeMenu'))
            # self.delete_menu()
            self.model.set('activeMenu', value=None)
            return True
        elif event == "-MENU-ADD-RECIPE-":
            if self.model.get('activeMenu') == None or self.model.get('activeMenuDay') == None:
                sg.PopupError('No Menu Selected!', title='Error')
                return True
            self.add_recipe()
            self.save_menu(self.model.get('activeMenu'))
            return True
        elif event == "-MENU-DAY-":
            self.model.set('activeMenuDay', value=self.model.get('activeMenu').getDay(values['-MENU-DAY-']))
            return True
        elif event == "-MENU-SAVE-":
            self.save_menu(self.model.get('activeMenu'), update_name = values['-MENU-NAME-'])
            return True
        elif event.find('Delete::menu//') != -1:
            group = event.split('//')[1]
            try:
                recipe = self.find_recipe_from_table(event, values)
            except ValueError:
                sg.PopupError('No Recipe Selected!')
                return True
            date = self.model.get('activeMenuDay')
            self.model.get('activeMenu').removeRecipe(recipe, date, group)
            self.model.notifyOberservers('activeMenuDay')
            return True
        elif event.find('Edit::menu//') != -1:
            try:
                recipe = self.find_recipe_from_table(event, values)
            except ValueError:
                sg.PopupError('No Recipe Selected!')
                return True
            self.model.set('activeRecipe', value=recipe)
            self.model.set('active_view', value='-EDITOR-')
            return True
        elif event.find('View::menu//') != -1:
            try:
                recipe = self.find_recipe_from_table(event, values)
            except ValueError:
                sg.PopupError('No Recipe Selected!')
                return True
            self.model.set('activeRecipe', value=recipe)
            self.model.set('active_view', value='-VIEWER-')
            return True
        return False

    def find_recipe_from_table(self, event, values):
        tableKey = event.split('//')[1]
        day_menu = self.model.get('activeMenuDay')
        if len(values[tableKey]) <= 0:
            raise ValueError('No Recipe Selected')
        recipe_index = values[tableKey][0]
        recipe = day_menu.get(tableKey.lower())[recipe_index]
        return recipe

    def save_menu(self, menu, update_name=None):
        if menu == None:
            logger.debug('A NoneType menu was given to save_menu, aborting...')
            return

        if self.model.get('MenuAPI').menuExists(menu):
            self.model.get('MenuAPI').deleteMenu(menu)
            if update_name is not None and update_name != menu.getName():
                menu.name = update_name
            try:
                self.model.get('MenuAPI').saveMenu(menu)
            except:
                sg.PopupError('Error occured during saving', title='Error')
                logger.debug(f"Unexpected error:{sys.exc_info()[0].__str__()}")
                return
        else:
            try:
                self.model.get('MenuAPI').saveMenu(menu)
            except:
                sg.PopupError('Error occured during saving', title='Error')
                logger.debug(f"Unexpected error:{sys.exc_info()[0].__str__()}")
                return
        self.model.set('activeMenu', value=menu)

    def shopping_modal(self):
        layout = [
            [sg.Multiline(self.model.get('activeMenu').shopping.__str__(), size=(50,30))],
            [sg.Button('Close')]
        ]

        window = sg.Window('Shopping List', layout, finalize=True, modal=True)

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "Close"):
                break

        window.close()

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
             sg.Combo(values=list(self.model.get('activeMenuDay').data.keys()),
                      key='-MODAL-GROUP-', default_value='other')],
            [sg.Button('Add', key="-MODAL-ADD-"),
             sg.Button('Cancel', key="-MODAL-CANCEL-")]
        ]

        window = sg.Window('Select Menu', layout, finalize=True, modal=True)
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
                try:
                    self.model.get('activeMenu').addRecipe(rec=rec*mult, date=date, group=group)
                except:
                    logger.debug('Error occured during addRecipe function')
                    sg.PopupError('An error has occured. Recipe not added.')
                    break
                self.model.notifyOberservers('activeMenuDay')
                break

        window.close()

    def display_missing_recipes(self):
        menu = self.model.get('activeMenu')
        if len(menu.missing_recipes) > 0:
            missing = '\n'.join([rec for rec in menu.missing_recipes])
            sg.popup_ok(f'Some recipes could not be found:\n{missing}')

    def select_menu_modal(self):
        search = searchBar.searchBar(key='-MODAL-SEARCH-', api=self.model.get('MenuAPI'), length=20, searchbutton=False)
        layout = [
            [search],
            [sg.Button('Open', key="-MODAL-OPEN-"),
             sg.Button('Add New', key="-MODAL-NEW-"),
             sg.Button('Cancel', key="-MODAL-CANCEL-")]
        ]

        window = sg.Window('Select Menu', layout, finalize=True, modal=True)
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

        window = sg.Window('New Menu', layout, finalize=True, modal=True)
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
                self.model.set('activeMenuDay', value=new_menu.getDay(0))
                break
            if not set_name:
                start = window['-MODAL-START-'].get()
                end = window['-MODAL-END-'].get()
                window['-MODAL-NAME-'].update(value=f'{start}{Menu.menu.date_delimiter}{end}')

        window.close()
