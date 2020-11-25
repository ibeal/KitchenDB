from database import *
from apiCalls import *
from views.view import view

class KitchenModel:
    __instance = None
    @staticmethod
    def getInstance(caller=None):
        """ Static access method. """
        # if caller and isinstance(caller, view):
        if caller:
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
            self.window = window
            self.data = {}
            self.data["controllers"] = {}
            self.data["tabData"] = {}
            self.data["activeRecipe"] = None
            self.data["recipe_table"] = None
            self.data["views"] = {'-TABS-':None, '-TABLE-':None, '-EDITOR-':None, '-VIEWER-':None, '-MENU-':None, '-INVENTORY-':None}
            self.data["active_view"] = None
            self.data["state"] = {"lastTableAction": "default"}
            self.data["db"] = database()
            self.data["api"] = apiCalls()
            self.data["prefs"] = None
            self.data["observers"] = []
            self.data["prefFile"] = 'userSettings.config'

    def set(self, key, value):
        self.data[key] = value
        self.notifyOberservers(key)

    def setView(self, key, value):
        self.data["views"][key] = value
        self.notifyOberservers(key)

    def setState(self, key, value):
        self.data["state"][key] = value
        self.notifyOberservers()

    def setPref(self, key, value):
        self.data["prefs"][key] = value
        self.notifyOberservers()

    def get(self, key):
        return self.data[key]

    def getView(self, key):
        return self.data["views"][key]

    def getState(self, key):
        return self.data["state"][key]

    def getPref(self, key):
        return self.data["prefs"][key]

    def notifyOberservers(self, key=None):
        for ob in self.data["observers"]:
            ob.refreshView(self.__instance, key)
