import logging, os.path, json
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from DB.database import *
from containers.recipe import recipe
from apiCalls import *
from views import recipeEditor as editor
from views import recipeTable as tableTab
from views import recipeViewer as viewer
from views import menuEditor
from KitchenModel import *
from MainController import *
logger = logging.getLogger('mainGui Log')

class gui:

    def __init__(self, android=False):
        self.android = android
        logger.debug('Creating Database and API units for mainGui...')
        self.model = KitchenModel.getInstance()
        # self.model.db = database()
        # self.api = apiCalls()

        logger.debug('Setting configuations...')
        self.recFields = {field: f'-{field}-BOX-' for field in recipe.pretty_fields}
        self.recTableDim = (20,6)
        self.tableData = None
        self.model.set('prefs', value=self.importPrefs(), merge=True)
        sg.theme(self.model.get('prefs')['theme'])

        self.expands = {'x':[], 'y':[], 'xy':[]}
        self.menu_def = [['&File', ['Import Recipe', 'Import Database', '---', 'E&xit'  ]],
        ['&Edit', ['Preferences'],],
        ['&Help', '&About...'],]
        # self.state = {"lastTableAction": "default"}

        # self.model.set('views', value={'-TABS-':None, '-TABLE-':None, '-EDITOR-':None, '-VIEWER-':None, '-MENU-':None, '-INVENTORY-':None})
        self.recTable = '-RECIPE-TABLE-'
        logger.debug('Creating Table...')
        # part of the tab creation is adding itself to the model
        self.model.addObserver(tableTab.recipeTable('Recipe Table', master=self, key='-TABLE-', tableKey=self.recTable))

        self.ingTable = '-OPTION-TABLE-'
        logger.debug('Creating Editor...')
        self.model.addObserver(editor.recipeEditor('Recipe Editor', master=self, key='-EDITOR-', ingTableKey=self.ingTable))

        self.model.addObserver(menuEditor.menuEditor('Menu Editor', master=self, key='-MENU-'))

        self.model.addObserver(viewer.recipeViewer('Recipe Viewer', master=self, key='-VIEWER-'))
        self.model.set('views', '-TABS-', value=sg.TabGroup([
            [self.model.get('views')['-TABLE-']],
            [self.model.get('views')['-EDITOR-']],
            [self.model.get('views')['-VIEWER-']],
            [self.model.get('views')['-MENU-']]
        ], key="-TABS-"))
        # self.expands['xy'].append(self.model.get('views', ('-TABS-'))

        # Tabbed Layout
        layout = [
            [sg.Menu(self.menu_def)],
            [self.model.get('views')['-TABS-']]
        ]

        logger.debug('Creating window...')
        if android:
            self.window = sg.Window('KitchenDB',
                                    layout,
                                    finalize=True,
                                    size=(800,1280),
                                    location=(0,0))
        else:
            self.window = sg.Window('KitchenDB',
                                    layout,
                                    finalize=True,
                                    resizable=True)
        self.controller = MainController(self.window)
        self.model.window = self.window

    def importPrefs(self):
        if not os.path.exists(self.model.get('prefFile')):
            logger.debug('config not found, using default')
            return self.model.get('prefs')
        with open(self.model.get('prefFile'), 'r') as f:
            logger.debug('config found, using custom settings')
            return json.load(f)

def main(**kwargs):
    g = gui(**kwargs)
    # g = gui(True)
    g.controller.mainLoop()

if __name__ == '__main__':
    main()
