import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
# import KitchenGUI.searchBar as searchBar
from DB.database import *
from containers.recipe import *
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
        def menu_table(key, heading, width=50, rows=7):
            click_menu = [
            ['menu'],
            [f'&View::menu//{key}',
            f'&Edit::menu//{key}',
            f'&Delete::menu//{key}']
            ]
            return sg.Table(values=[['']], key=key, headings=[heading], num_rows=rows,
            enable_events=True, auto_size_columns=False, col_widths=[width],
            hide_vertical_scroll=True, right_click_menu=click_menu)
        layout = [
                [sg.T('Menu'),
                 sg.In('', key="-MENU-NAME-", size=(20,1)),
                 sg.Button('Select Menu', key="-MENU-SELECT-"),
                 sg.Button('Delete Menu', key="-MENU-DELETE-", disabled=True),
                 sg.Button('Shopping List', key="-MENU-SHOPPING-", disabled=True),
                 sg.Button('Add Recipe', key="-MENU-ADD-RECIPE-", disabled=True),
                 sg.Button('Save', key="-MENU-SAVE-", disabled=True)],
                [sg.T('Menu for: '),
                 sg.Combo(values=[], default_value='', key="-MENU-DAY-", size=(15,1), enable_events=True)],
                [menu_table('BREAKFAST', 'Breakfast')],
                [menu_table("LUNCH", 'Lunch')],
                [menu_table("DINNER", 'Dinner')],
                [menu_table("OTHER", 'Other')],
        ]
        return layout

    def fillFields(self, day):
        self.model.window['-MENU-SAVE-'].update(disabled=False)
        self.model.window['-MENU-DELETE-'].update(disabled=False)
        self.model.window['-MENU-SHOPPING-'].update(disabled=False)
        self.model.window['-MENU-ADD-RECIPE-'].update(disabled=False)
        # keys = list(menu.menus.keys())
        # firstDay = menu.getDay(0)
        # self.model.window["-MENU-NAME-"].update(value=menu.name)
        self.model.window["-MENU-DAY-"].update(value=day.date)

        breakfast = [[rec.getID()] for rec in day.get('breakfast')]
        self.model.window["BREAKFAST"].update(values=breakfast)

        lunch = [[rec.getID()] for rec in day.get('lunch')]
        self.model.window["LUNCH"].update(values=lunch)

        dinner = [[rec.getID()] for rec in day.get('dinner')]
        self.model.window["DINNER"].update(values=dinner)

        other = [[rec.getID()] for rec in day.get('other')]
        self.model.window["OTHER"].update(values=other)

    def loadMenu(self, menu):
        keys = list(menu.menus.keys())
        firstDay = menu.getDay(0)
        self.model.window["-MENU-NAME-"].update(value=menu.name)
        self.model.window["-MENU-DAY-"].update(values=keys)
        # self.fillFields(firstDay)

    def clearMenu(self):
        self.model.window['-MENU-SAVE-'].update(disabled=True)
        self.model.window['-MENU-DELETE-'].update(disabled=True)
        self.model.window['-MENU-SHOPPING-'].update(disabled=True)
        self.model.window['-MENU-ADD-RECIPE-'].update(disabled=True)
        self.model.window["-MENU-NAME-"].update(value='')
        self.model.window["-MENU-DAY-"].update(values=[], value='')
        self.model.window["BREAKFAST"].update(values=[['']])
        self.model.window["LUNCH"].update(values=[['']])
        self.model.window["DINNER"].update(values=[['']])
        self.model.window["OTHER"].update(values=[['']])

    def clearFields(self):
        self.model.window["BREAKFAST"].update(values=[['']])
        self.model.window["LUNCH"].update(values=[['']])
        self.model.window["DINNER"].update(values=[['']])
        self.model.window["OTHER"].update(values=[['']])
