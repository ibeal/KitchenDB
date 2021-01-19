import logging
import os.path
import json
import PySimpleGUI as sg
from KitchenModel import KitchenModel
# from DB.database import database
from containers.recipe import recipe
# from apiCalls import apiCalls
# from views import recipeEditor as editor
# from views import recipeTable as tableTab
# from views import recipeViewer as viewer
logger = logging.getLogger('MainController Log')

class MainController:
    def __init__(self, window=None, model=None):
        self.window = window
        self.model = KitchenModel.getInstance()

    def mainLoop(self, window=None):
        # if given window, use that window for this function
        # and restore the old window at the end
        self.model.beginNotify()
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
            # logger.debug(f'value is {values}')

            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if self.model.get("controllers", values['-TABS-']).handle(event, values):
                continue
            elif event == 'Preferences':
                # self.window.disable()
                self.prefEditor()
                # self.window.enable()
            elif event == 'Import Recipe':
                # import recipe
                recipe_files = sg.popup_get_file('Enter a recipe file...', multiple_files=True)
                if not recipe_files:
                    continue
                recipe_files = recipe_files.split(';')
                for file in recipe_files:
                    new_rec = recipe(file=file)
                    if self.model.get('RecipeAPI').recipeExists(new_rec):
                        if sg.popup_yes_no("This recipe already exists, do you want to overwrite it?", title="Overwrite?"):
                            # save to db
                            self.model.get('RecipeAPI').deleteRecipe(new_rec)
                            self.model.get('RecipeAPI').saveRecipe(new_rec)
                    else:
                        self.model.get('RecipeAPI').saveRecipe(new_rec)
                self.model.get('views')['-TABLE-'].Select()
                self.model.notifyOberservers('recipe import')
                # self.model.get('views')['-TABLE-'].refreshRecipeTable()
            elif event == 'Import Database':
                # import database
                pass

        self.window.close()
        if window:
            self.window = windowBackup

    def switchTabs(self, tab):
        self.model.get('views')[tab].Select()
        # self.model.set('active_view', value=tab)

    def deferHandle(self, tab, event, values):
        return self.model.get('controllers')[tab].handle(event, values)

    def activateRecipe(self, rec):
        self.model.set("activeRecipe", value=rec)

    def savePrefs(self):
        with open(self.model.get('prefFile'), 'w') as f:
            json.dump(self.model.get("prefs"), f)

    def prefEditor(self):
        layout = [[sg.Text('Theme Browser (Themes change on app restart)')],
          [sg.Combo(values=sg.theme_list(),
                    size=(20, 12), key='-LIST-', enable_events=True),
           sg.Button('View Themes')
          ],
          [sg.Text('Recipe Export Folder')],
          [
            sg.In(key='-PREF-FOLDER-'),
            sg.FolderBrowse('Browse', initial_folder=self.model.get('prefs')['recipeFolder'])
          ],
          [sg.Text('Database Location')],
          [
            sg.In(key='-DB-LOCATION-'),
            sg.FileBrowse('Browse', initial_folder=self.model.get('prefs')['dbLocation'])
          ],
          [sg.Button('Close'), sg.Button('Apply')]]

        window = sg.Window('Theme Browser', layout, finalize=True, modal=True)
        window['-LIST-'].update(self.model.get('prefs')['theme'])
        window['-PREF-FOLDER-'].update(self.model.get('prefs')['recipeFolder'])
        window['-DB-LOCATION-'].update(self.model.get('prefs')['dbLocation'])

        while True:
            event, values = window.read()
            logger.debug(f'prefEditor event is {event}')
            logger.debug(f'prefEditor value is {values}')
            if event in (sg.WIN_CLOSED, 'Close'):
                break
            elif event == '-LIST-':
                logger.debug(f'list value is {values["-LIST-"]}')
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
