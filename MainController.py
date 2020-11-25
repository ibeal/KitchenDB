import logging, os.path, json
from KitchenModel import *
from database import *
from recipeCreator import recipe
from apiCalls import *
from KitchenGUI import recipeEditor as editor
from KitchenGUI import recipeTable as tableTab
from KitchenGUI import recipeViewer as viewer
import PySimpleGUI as sg

class MainController:
    def __init__(self, window=None, model=None):
        self.window = window
        self.model = model if model else KitchenModel.getInstance()

    def mainLoop(self, window=None):
        # if given window, use that window for this function
        # and restore the old window at the end
        if window:
            windowBackup = self.window
            self.window = window

        if not self.window:
            raise Exception("mainLoop called on MainController with no window specified!")
        # do stuff
        logger.debug('Main Loop Started')
        while True:
            event, values = self.window.read()
            logger.debug(f'event was {event}')
            logger.debug(f'value is {values}')

            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if self.model.getView(values['-TABS-']).controller.handle(event, values):
                continue
            elif event == '-RECIPE-TABLE-':
                self.model.getView('-VIEWER-').Select()
                self.activateRecipe(self.model.getView('-TABLE-').tableData[values['-RECIPE-TABLE-'][0]])
            elif event == '-SAVE-RECIPE-':
                # self.saveFields()
                self.model.getView('-TABLE-').refreshRecipeTable()
            elif event == '-DELETE-RECIPE-':
                # self.model.getView('-EDITOR-').deleteRecipe()
                self.model.getView('-TABLE-').Select()
                self.model.getView('-TABLE-').refreshRecipeTable()
            elif event == '-VIEW-RECIPE-':
                rec = self.model.getView('-EDITOR-').getFields()
                self.activateRecipe(rec)
                self.model.getView('-VIEWER-').Select()
            elif event == '-VIEWER-EDIT-':
                self.model.getView('-EDITOR-').Select()
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
                self.model.get('views')['-TABLE-'].Select()
                self.model.get('views')['-TABLE-'].refreshRecipeTable()
            elif event == 'Database':
                # import database
                pass

        self.window.close()
        if window:
            self.window = windowBackup

    def switchTabs(self, tab):
        self.model.get('views')[tab].Select()

    def deferHandle(self, tab, event, values):
        self.model.get('views')[tab].handle(event, values)

    def activateRecipe(self, rec):
        self.model.get('views')['-EDITOR-'].fillFields(rec)
        self.model.get('views')['-VIEWER-'].newRecipe(rec)

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
