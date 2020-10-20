import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from recipeCreator import *
logger = logging.getLogger('Debug Log')

class recipeViewer(sg.Tab):
    def __init__(self, title, master, *args, **kwargs):
        self.master = master
        self.activeRecipe = None
        self.recipeBox = sg.Multiline(key='-VIEWER-BOX-', size=(80,30))
        self.send = sg.Button('Send File', key='-VIEWER-SEND-')
        self.share = sg.Button('Share', key='-VIEWER-SHARE-')
        layout = [
            [
                 sg.Button('Print', key='-VIEWER-PRINT-'),
                 self.send,
                 self.share
            ],
            [self.recipeBox],
            [sg.HorizontalSeparator()],
            [sg.T('Nutrition')]
        ]
        super().__init__(title, layout=layout, *args, **kwargs)

    def handle(self, event, values):
        if event == '-VIEWER-PRINT-':
            return True
        elif event == '-VIEWER-SEND-':
            self.activeRecipe.outputToYaml(self.master.prefs['recipeFolder'] + 'test.yaml')
            return True
        elif event == '-VIEWER-SHARE-':
            self.activeRecipe.outputToTxt(self.master.prefs['recipeFolder'] + 'text.txt')
            return True
        return False

    def fillFields(self, rec):
        self.activeRecipe = rec
        self.recipeBox.update(rec.__str__())
