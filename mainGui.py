import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from database import *
from recipeCreator import recipe
from apiCalls import *
from KitchenGUI import recipeEditor as editor
from KitchenGUI import recipeTable as tableTab
from KitchenGUI import recipeViewer as viewer
logger = logging.getLogger('Debug Log')

class gui:

    def __init__(self):
        logger.debug('Creating Database and API units for mainGui...')
        self.db = database()
        self.api = apiCalls()

        logger.debug('Setting configuations...')
        self.recFields = {field: f'-{field}-BOX-' for field in recipe.pretty_fields}
        self.recTableDim = (20,6)
        self.tableData = None
        self.prefs = {'recipeFolder': '.\\recipes\\', 'theme': 'Dark Blue 1'}
        sg.theme(self.prefs['theme'])

        self.expands = {'x':[], 'y':[], 'xy':[]}
        self.menu_def = [['&File', ['&Open', '&Save', '---', 'Properties', 'E&xit'  ]],
        ['&Edit', ['Paste', ['Special', 'Normal',], 'Undo'],],
        ['&Help', '&About...'],]
        self.state = {"lastTableAction": "default"}

        self.panes = {'-TABS-':None, '-TABLE-':None, '-EDITOR-':None, '-VIEWER-':None, '-MENU-':None, '-INVENTORY-':None}
        self.recTable = '-RECIPE-TABLE-'
        logger.debug('Creating Table...')
        self.panes['-TABLE-'] = tableTab.recipeTable('Recipe Table', master=self, key='-TABLE-', tableKey=self.recTable)

        self.ingTable = '-OPTION-TABLE-'
        logger.debug('Creating Editor...')
        self.panes['-EDITOR-'] = editor.recipeEditor('Recipe Editor', master=self, key='-EDITOR-', ingTableKey=self.ingTable)

        self.panes['-VIEWER-'] = viewer.recipeViewer('Recipe Viewer', master=self, key='-VIEWER-')
        self.panes['-TABS-'] = sg.TabGroup([
            [self.panes['-TABLE-']],
            [self.panes['-EDITOR-']],
            [self.panes['-VIEWER-']]
        ], key="-TABS-")
        self.tabHolder = self.panes['-TABS-']
        self.expands['xy'].append(self.tabHolder)

        # Tabbed Layout
        layout = [
            [sg.Menu(self.menu_def)],
            [self.panes['-TABS-']]
        ]

        logger.debug('Creating window...')
        self.window = sg.Window('KitchenDB',
                                layout,
                                finalize=True,
                                resizable=True)

    def mainLoop(self):
        logger.debug('Main Loop Started')
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if self.panes[values['-TABS-']].handle(event, values):
                continue
            elif event == '-RECIPE-TABLE-':
                self.panes['-EDITOR-'].Select()
                self.activateRecipe(self.panes['-TABLE-'].tableData[values['-RECIPE-TABLE-'][0]])
            elif event == '-SAVE-RECIPE-':
                # self.saveFields()
                self.panes['-TABLE-'].refreshRecipeTable()
            elif event == '-DELETE-RECIPE-':
                # self.panes['-EDITOR-'].deleteRecipe()
                self.panes['-TABLE-'].Select()
                self.panes['-TABLE-'].refreshRecipeTable()
            elif event == '-VIEW-RECIPE-':
                rec = self.panes['-EDITOR-'].getFields()
                self.activateRecipe(rec)
                self.panes['-VIEWER-'].Select()

        self.window.close()

    def switchTabs(self, tab):
        self.panes[tab].Select()

    def deferHandle(self, tab, event, values):
        self.panes[tab].handle(event, values)

    def activateRecipe(self, rec):
        self.panes['-EDITOR-'].fillFields(rec)
        self.panes['-VIEWER-'].fillFields(rec)


def main():
    g = gui()
    g.mainLoop()

if __name__ == '__main__':
    main()
