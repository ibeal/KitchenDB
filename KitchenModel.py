from database import *
from apiCalls import *

class KitchenModel:
    __instance = None
    @staticmethod
    def getInstance(caller=None):
        """ Static access method. """
        if caller:
            self.observees.append(caller)
        if KitchenModel.__instance == None:
            KitchenModel()
        return KitchenModel.__instance
    def __init__(self):
        """ Virtually private constructor. """
        if KitchenModel.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            KitchenModel.__instance = self
            self.data = {}
            self.data["activeRecipe"] = None
            self.data["recipe_table"] = None
            self.data["panes"] = {'-TABS-':None, '-TABLE-':None, '-EDITOR-':None, '-VIEWER-':None, '-MENU-':None, '-INVENTORY-':None}
            self.data["active_pane"] = None
            self.data["state"] = {"lastTableAction": "default"}
            self.data["db"] = database()
            self.data["api"] = apiCalls()
            self.data["prefs"] = None
            self.data["observees"] = []
            self.data["prefFile"] = 'userSettings.config'

    def set(self, key, value):
        self.data[key] = value
        self.notifyOberservers(key)

    def setPane(self, key, value):
        self.data["panes"][key] = value
        self.notifyOberservers(key)

    def setState(self, key, value):
        self.data["state"][key] = value
        self.notifyOberservers()

    def setPref(self, key, value):
        self.data["prefs"][key] = value
        self.notifyOberservers()

    def get(self, key):
        return self.data[key]

    def getPane(self, key):
        return self.data["panes"][key]

    def getState(self, key):
        return self.data["state"][key]

    def getPref(self, key):
        return self.data["prefs"][key]

    def notifyOberservers(self, key=None):
        pass
        # for ob in self.observees:
        #     ob.updateView(self.__instance)
