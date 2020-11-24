from database import *
from apiCalls import *

class KitchenModel:
   __instance = None
   @staticmethod
   def getInstance():
      """ Static access method. """
      if KitchenModel.__instance == None:
         KitchenModel()
      return KitchenModel.__instance
   def __init__(self):
      """ Virtually private constructor. """
      if KitchenModel.__instance != None:
         raise Exception("This class is a singleton!")
      else:
         KitchenModel.__instance = self
         self.activeRecipe = None
         self.recipe_table = None
         self.panes = {'-TABS-':None, '-TABLE-':None, '-EDITOR-':None, '-VIEWER-':None, '-MENU-':None, '-INVENTORY-':None}
         self.active_pane = None
         self.state = {"lastTableAction": "default"}
         self.db = database()
         self.api = apiCalls()
         self.prefs = None
