import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from DB.database import *
from recipeCreator import *
from apiCalls import *
from KitchenModel import *
from controllers.controller import controller
logger = logging.getLogger('menuEditorController Log')

class menuEditorController(controller):
    def __init__(self):
        pass

    def setup(self):
        pass

    def handle(self, event, values):
        pass
