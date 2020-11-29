from DB.database import *
from DB.RecipeAPI import *
from apiCalls import *
from views.view import view
import os

class KitchenModel:
    __instance = None
    @staticmethod
    def getInstance(caller=None):
        """ Static access method. """
        if caller and isinstance(caller, view):
        # if caller:
            self.data["observers"].append(caller)
        if KitchenModel.__instance == None:
            KitchenModel()
        return KitchenModel.__instance
    def __init__(self, window=None):
        """ Virtually private constructor. """
        if KitchenModel.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            KitchenModel.__instance = self
            self.notify = False
            self.window = window
            self.data = {}
            self.data["controllers"] = {}
            self.data["tabData"] = {}
            self.data["activeRecipe"] = None
            self.data["recipe_table"] = None
            self.data["views"] = {'-TABS-':None, '-TABLE-':None, '-EDITOR-':None, '-VIEWER-':None, '-MENU-':None, '-INVENTORY-':None}
            self.data["active_view"] = '-TABLE-'
            self.data["state"] = {"lastTableAction": "default"}
            self.data["db"] = database()
            self.data["RecipeAPI"] = RecipeAPI(self.data["db"])
            self.data["api"] = apiCalls()
            self.data["prefs"] = {
                'recipeFolder': os.getcwd() + '/recipes/',
                'theme': 'Dark Blue 1',
                'dbLocation': os.getcwd() + '/KitchenDB'}
            self.data["observers"] = []
            self.data["prefFile"] = 'userSettings.config'

    def beginNotify(self):
        self.notify = True

    def endNotify(self):
        self.notify = False

    def addTab(self, key, view, controller, tabData):
        self.data["tabData"][key] = tabData
        self.data["views"][key] = view
        controller.setup()
        self.data["controllers"][key] = controller

    def addObserver(self, observer):
        self.data["observers"].append(observer)

    def set(self, *args, value=None, notify=True, merge=False):
        if len(args) <= 0:
            raise Exception("Tried to set value in model, but no key given")
        elif len(args) == 1:
            if merge and isinstance(value, dict):
                self.data[args[0]] = {**self.data[args[0]], **value}
            else:
                self.data[args[0]] = value
        else:
            self.data[args[0]] = self.setHelper(self.data[args[0]], value, *args[1:])
        if notify and self.notify:
            self.notifyOberservers(args[0])

    def setHelper(self, data, value, *args):
        if len(args) <= 1:
            data[args[0]] = value
            return data
        data[args[0]] = self.setHelper(data[args[0]], value, *args[1:])
        return data

    def get(self, *args):
        data = self.data
        for arg in args:
            data = data[arg]
        return data

    def notifyOberservers(self, key=None):
        for ob in self.data["observers"]:
            ob.refreshView(self.__instance, key)
