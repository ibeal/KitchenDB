import logging
import numpy as np
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from recipeCreator import *
from KitchenModel import *
from views.view import view
from controllers.recipeViewerController import *
logger = logging.getLogger('recipeViewer log')

class recipeViewer(sg.Tab, view):
    def __init__(self, title, master, *args, **kwargs):
        self.master = master
        self.model = KitchenModel.getInstance()
        self.recipeBox = sg.Multiline(key='-VIEWER-BOX-', size=(80,30),
                tooltip="Recipes will be displayed here when they are selected on the recipe table tab.")
        self.export = sg.Button('Export File', key='-VIEWER-EXPORT-',
                tooltip="This button causes a prompt to display that will allow you to create a recipe file")
        self.share = sg.Button('Share', key='-VIEWER-SHARE-', disabled=True,
                tooltip="This button will allow you to quickly share recipes with friends - Not In Use")
        self.multby = sg.Combo(values=[f'{i}' for i in np.arange(.5,5,.5)], key='-VIEWER-MULTBY-',
                enable_events=True, default_value='1')
        layout = [
            [
                 sg.Button('Print', key='-VIEWER-PRINT-', disabled=True,
                        tooltip="This button will let you print the currently selected recipe"),
                 self.export,
                 self.share,
                 sg.Button('Edit', key='-VIEWER-EDIT-',
                        tooltip="Click here to edit this recipe"),
                sg.T('Multiply By:'),
                self.multby
            ],
            [self.recipeBox],
            [sg.HorizontalSeparator()],
            [sg.T('Nutrition', tooltip="This area will be filled with Nutrition info about the recipe - Not In Use")]
        ]
        super().__init__(title, layout=layout, *args, **kwargs)
        # self.controller = recipeViewerController(self.recipeBox)
        self.model.addTab("-VIEWER-", self, recipeViewerController(), {"recipeBox":self.recipeBox})

    def refreshView(self, model, key):
        if key == "activeRecipe":
            if self.model.get('activeRecipe') == None:
                self.clearFields()
            else:
                self.newRecipe(self.model.get('activeRecipe'))
        elif key == "active_view":
            if self.model.get("active_view") == "-VIEWER-":
                self.Select()

    # def handle(self, event, values):
    #     if event == '-VIEWER-PRINT-':
    #         if self.model.get('activeRecipe') == None:
    #             sg.PopupError("No recipe selected!", title="No Recipe")
    #             return True
    #         return True
    #     elif event == '-VIEWER-EXPORT-':
    #         if self.model.get('activeRecipe') == None:
    #             sg.PopupError("No recipe selected!", title="No Recipe")
    #             return True
    #         self.exportModal(self.model.get('activeRecipe'))
    #         return True
    #     elif event == '-VIEWER-SHARE-':
    #         if self.model.get('activeRecipe') == None:
    #             sg.PopupError("No recipe selected!", title="No Recipe")
    #             return True
    #         # self.model.get('activeRecipe').outputToTxt(self.model.get('prefs', 'recipeFolder') + 'text.txt')
    #         return True
    #     elif event == '-VIEWER-EDIT-':
    #         # navigate to editor tab
    #         if self.model.get('activeRecipe') == None:
    #             sg.PopupError("No recipe selected!", title="No Recipe")
    #             return True
    #         return False
    #     elif event == '-VIEWER-MULTBY-':
    #         if self.model.get('activeRecipe') == None:
    #             sg.PopupError("No recipe selected!", title="No Recipe")
    #             self.multby.update('1')
    #             return True
    #         self.fillFields(recipe(copyme=self.model.get('activeRecipe')) * float(values['-VIEWER-MULTBY-']))
    #         return True
    #     return False

    def fillFields(self, rec):
        self.recipeBox.update(rec.__str__())

    def clearFields(self):
        self.recipeBox.update(" ")

    def resetMult(self):
        self.multby.update('1')

    def newRecipe(self, rec):
        self.resetMult()
        self.fillFields(rec)

    def exportModal(self, rec):
        defaultType = 'txt'
        types = {'txt': ('Text Files', '*.txt'),
                 'pdf': ('PDF Files', '*.pdf'),
                 'json':('JSON Files', '*.json'),
                 'yaml':('YAML Files', '*.yaml')}
        recTitle = rec.title.replace(' ', '-')
        defaultSave = self.model.get('prefs', 'recipeFolder') + recTitle + f'.{defaultType}'
        layout = [[sg.Text('Export Details')],
          [
            sg.T('Destination'),
            sg.In(default_text=defaultSave, key='-EXPORT-FOLDER-'),
            sg.FileSaveAs('Browse',
                initial_folder=self.model.get('prefs', 'recipeFolder'))
          ],
          [
            sg.T('Format'),
            sg.Combo(default_value=defaultType, values=['txt', 'pdf', 'yaml', 'json'],
                    size=(20, 12), key='-FORMAT-LIST-', enable_events=True)
          ],
          [sg.Button('Export'), sg.Button('Cancel')]]

        window = sg.Window('Export Details', layout)

        while True:
            event, values = window.read()
            # logger.debug(f'prefEditor event is {event}')
            if event in (sg.WIN_CLOSED, 'Cancel'):
                break
            elif event == '-FORMAT-LIST-':
                new_type = values['-FORMAT-LIST-']
                new_fname = values['-EXPORT-FOLDER-'].split('.')
                new_fname[-1] = new_type
                new_fname = '.'.join(new_fname)
                window['-EXPORT-FOLDER-'].update(value=new_fname)
            elif event == 'Export':
                # logger.debug(f'list value is {values["-LIST-"]}')
                self.exportFile(rec, type=values['-FORMAT-LIST-'], location=values['-EXPORT-FOLDER-'])
                break
            elif event == 'Cancel':
                break

        window.close()

    def exportFile(self, rec, type, location):
        with open(location, 'w') as f:
            if type == 'PDF':
                # for now will be the same as txt
                f.write(rec.__str__())
            elif type == 'txt':
                f.write(rec.__str__())
            elif type == 'yaml':
                f.write('---\n')
                yaml.dump(rec.outputToYaml(), f)
