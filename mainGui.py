import logging, os.path, json
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
        self.prefFile = 'userSettings.config'
        self.prefs = self.importPrefs()
        sg.theme(self.prefs['theme'])

        self.expands = {'x':[], 'y':[], 'xy':[]}
        self.menu_def = [['&File', ['Import...', ['Recipe', 'Database'], '&Save', '---', 'E&xit'  ]],
        ['&Edit', ['Preferences'],],
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
        # self.expands['xy'].append(self.tabHolder)

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
            logger.debug(f'event was {event}')
            logger.debug(f'value is {values}')

            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if self.panes[values['-TABS-']].handle(event, values):
                continue
            elif event == '-RECIPE-TABLE-':
                self.panes['-VIEWER-'].Select()
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
            elif event == '-VIEWER-EDIT-':
                self.panes['-EDITOR-'].Select()
            elif event == 'Preferences':
                self.window.disable()
                self.prefEditor()
                self.window.enable()
            elif event == 'Recipe':
                # import recipe
                recipe_files = sg.popup_get_file('Enter a recipe file...', multiple_files=True).split(';')
                for file in recipe_files:
                    new_rec = recipe(file=file)
                    if self.db.recipeExists(new_rec):
                        if sg.popup_yes_no("This recipe already exists, do you want to overwrite it?", title="Overwrite?"):
                            # save to db
                            self.db.deleteRecipe(new_rec)
                            self.db.saveRecipe(new_rec)
                    else:
                        self.db.saveRecipe(new_rec)
                self.panes['-TABLE-'].Select()
                self.panes['-TABLE-'].refreshRecipeTable()
            elif event == 'Database':
                # import database
                pass


        self.window.close()

    def switchTabs(self, tab):
        self.panes[tab].Select()

    def deferHandle(self, tab, event, values):
        self.panes[tab].handle(event, values)

    def activateRecipe(self, rec):
        self.panes['-EDITOR-'].fillFields(rec)
        self.panes['-VIEWER-'].newRecipe(rec)

    def savePrefs(self):
        with open(self.prefFile, 'w') as f:
            json.dump(self.prefs, f)

    def importPrefs(self):
        if not os.path.exists(self.prefFile):
            logger.debug('config not found, using default')
            return {'recipeFolder': os.getcwd() + '/recipes/', 'theme': 'Dark Blue 1'}
        with open(self.prefFile, 'r') as f:
            logger.debug('config found, using custom settings')
            return json.load(f)

    def prefEditor(self):

        layout = [[sg.Text('Theme Browser (Themes change on app restart)')],
          [sg.Combo(values=sg.theme_list(),
                    size=(20, 12), key='-LIST-', enable_events=True),
           sg.Button('View Themes')
          ],
          [
            sg.In(key='-PREF-FOLDER-'),
            sg.FolderBrowse('Browse', initial_folder=self.prefs['recipeFolder'])
          ],
          [sg.Button('Close'), sg.Button('Apply')]]

        window = sg.Window('Theme Browser', layout, finalize=True)
        window['-LIST-'].update(self.prefs['theme'])
        window['-PREF-FOLDER-'].update(self.prefs['recipeFolder'])

        while True:
            event, values = window.read()
            logger.debug(f'prefEditor event is {event}')
            logger.debug(f'prefEditor value is {values}')
            if event in (sg.WIN_CLOSED, 'Close'):
                break
            elif event == '-LIST-':
                # logger.debug(f'list value is {values["-LIST-"]}')
                self.prefs['theme'] = values['-LIST-']
                sg.theme(self.prefs['theme'])
            elif event == 'Apply':
                self.prefs['theme'] = values['-LIST-']
                self.prefs['recipeFolder'] = values['-PREF-FOLDER-']
                self.savePrefs()
            elif event == 'View Themes':
                sg.theme_previewer()

        if values != None:
            self.prefs['theme'] = values['-LIST-']
            self.prefs['recipeFolder'] = values['-PREF-FOLDER-']
            if self.prefs['recipeFolder'][-1] != '/':
                self.prefs['recipeFolder'] += '/'
            self.savePrefs()
        window.close()

def main():
    g = gui()
    g.mainLoop()

if __name__ == '__main__':
    main()
