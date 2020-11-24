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
from KitchenModel import *
logger = logging.getLogger('Debug Log')

class gui:

    def __init__(self):
        logger.debug('Creating Database and API units for mainGui...')
        self.model = KitchenModel.getInstance()
        # self.model.db = database()
        # self.api = apiCalls()

        logger.debug('Setting configuations...')
        self.recFields = {field: f'-{field}-BOX-' for field in recipe.pretty_fields}
        self.recTableDim = (20,6)
        self.tableData = None
        self.model.set('prefs', self.importPrefs())
        sg.theme(self.model.get('prefs')['theme'])

        self.expands = {'x':[], 'y':[], 'xy':[]}
        self.menu_def = [['&File', ['Import...', ['Recipe', 'Database'], '&Save', '---', 'E&xit'  ]],
        ['&Edit', ['Preferences'],],
        ['&Help', '&About...'],]
        # self.state = {"lastTableAction": "default"}

        # self.model.set('panes', {'-TABS-':None, '-TABLE-':None, '-EDITOR-':None, '-VIEWER-':None, '-MENU-':None, '-INVENTORY-':None})
        self.recTable = '-RECIPE-TABLE-'
        logger.debug('Creating Table...')
        self.model.setPane('-TABLE-', tableTab.recipeTable('Recipe Table', master=self, key='-TABLE-', tableKey=self.recTable))

        self.ingTable = '-OPTION-TABLE-'
        logger.debug('Creating Editor...')
        self.model.setPane('-EDITOR-', editor.recipeEditor('Recipe Editor', master=self, key='-EDITOR-', ingTableKey=self.ingTable))

        self.model.setPane('-VIEWER-', viewer.recipeViewer('Recipe Viewer', master=self, key='-VIEWER-'))
        self.model.setPane('-TABS-', sg.TabGroup([
            [self.model.get('panes')['-TABLE-']],
            [self.model.get('panes')['-EDITOR-']],
            [self.model.get('panes')['-VIEWER-']]
        ], key="-TABS-"))
        # self.expands['xy'].append(self.model.getPane('-TABS-'))

        # Tabbed Layout
        layout = [
            [sg.Menu(self.menu_def)],
            [self.model.get('panes')['-TABS-']]
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
            if self.model.getPane(values['-TABS-']).handle(event, values):
                continue
            elif event == '-RECIPE-TABLE-':
                self.model.getPane('-VIEWER-').Select()
                self.activateRecipe(self.model.getPane('-TABLE-').tableData[values['-RECIPE-TABLE-'][0]])
            elif event == '-SAVE-RECIPE-':
                # self.saveFields()
                self.model.getPane('-TABLE-').refreshRecipeTable()
            elif event == '-DELETE-RECIPE-':
                # self.model.getPane('-EDITOR-').deleteRecipe()
                self.model.getPane('-TABLE-').Select()
                self.model.getPane('-TABLE-').refreshRecipeTable()
            elif event == '-VIEW-RECIPE-':
                rec = self.model.getPane('-EDITOR-').getFields()
                self.activateRecipe(rec)
                self.model.getPane('-VIEWER-').Select()
            elif event == '-VIEWER-EDIT-':
                self.model.getPane('-EDITOR-').Select()
            elif event == 'Preferences':
                self.window.disable()
                self.prefEditor()
                self.window.enable()
            elif event == 'Recipe':
                # import recipe
                recipe_files = sg.popup_get_file('Enter a recipe file...', multiple_files=True).split(';')
                for file in recipe_files:
                    new_rec = recipe(file=file)
                    if self.model.db.recipeExists(new_rec):
                        if sg.popup_yes_no("This recipe already exists, do you want to overwrite it?", title="Overwrite?"):
                            # save to db
                            self.model.db.deleteRecipe(new_rec)
                            self.model.db.saveRecipe(new_rec)
                    else:
                        self.model.db.saveRecipe(new_rec)
                self.model.get('panes')['-TABLE-'].Select()
                self.model.get('panes')['-TABLE-'].refreshRecipeTable()
            elif event == 'Database':
                # import database
                pass


        self.window.close()

    def switchTabs(self, tab):
        self.model.get('panes')[tab].Select()

    def deferHandle(self, tab, event, values):
        self.model.get('panes')[tab].handle(event, values)

    def activateRecipe(self, rec):
        self.model.get('panes')['-EDITOR-'].fillFields(rec)
        self.model.get('panes')['-VIEWER-'].newRecipe(rec)

    def savePrefs(self):
        with open(self.model.get('prefFile'), 'w') as f:
            json.dump(self.model.get("prefs"), f)

    def importPrefs(self):
        if not os.path.exists(self.model.get('prefFile')):
            logger.debug('config not found, using default')
            return {'recipeFolder': os.getcwd() + '/recipes/', 'theme': 'Dark Blue 1'}
        with open(self.model.get('prefFile'), 'r') as f:
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
            sg.FolderBrowse('Browse', initial_folder=self.model.get('prefs')['recipeFolder'])
          ],
          [sg.Button('Close'), sg.Button('Apply')]]

        window = sg.Window('Theme Browser', layout, finalize=True)
        window['-LIST-'].update(self.model.get('prefs')['theme'])
        window['-PREF-FOLDER-'].update(self.model.get('prefs')['recipeFolder'])

        while True:
            event, values = window.read()
            logger.debug(f'prefEditor event is {event}')
            logger.debug(f'prefEditor value is {values}')
            if event in (sg.WIN_CLOSED, 'Close'):
                break
            elif event == '-LIST-':
                # logger.debug(f'list value is {values["-LIST-"]}')
                self.model.get('prefs')['theme'] = values['-LIST-']
                sg.theme(self.model.get('prefs')['theme'])
            elif event == 'Apply':
                self.model.get('prefs')['theme'] = values['-LIST-']
                self.model.get('prefs')['recipeFolder'] = values['-PREF-FOLDER-']
                self.savePrefs()
            elif event == 'View Themes':
                sg.theme_previewer()

        if values != None:
            self.model.get('prefs')['theme'] = values['-LIST-']
            self.model.get('prefs')['recipeFolder'] = values['-PREF-FOLDER-']
            if self.model.get('prefs')['recipeFolder'][-1] != '/':
                self.model.get('prefs')['recipeFolder'] += '/'
            self.savePrefs()
        window.close()

def main():
    g = gui()
    g.mainLoop()

if __name__ == '__main__':
    main()
