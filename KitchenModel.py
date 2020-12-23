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
            self.data["recipeUpdate"] = False

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
        """This is the global setter function, will take any number of unnamed arguments,
        this will generate the 'path' of the data to change, the value is the
        new value that the path will be given, notify is whether or not to notify
        the observer, merge is whether or not to merge the given dictionary or to
        overwrite the old one"""
        if len(args) <= 0:
            raise Exception("Tried to set value in model, but no key given")

        # base case: only one arg left, set or merge the value
        elif len(args) == 1:
            if merge and isinstance(value, dict):
                self.data[args[0]] = {**self.data[args[0]], **value}
            else:
                self.data[args[0]] = value
        # recursive case: more than one arg left, set first arg to return value
        # of the recursive call. Start recursion by calling helper
        else:
            self.data[args[0]] = self.setHelper(self.data[args[0]], value, *args[1:])

        # if we've started notifying and the bool is set to notify, then notify
        if notify and self.notify:
            self.notifyOberservers(args[0])

    def setHelper(self, data, value, *args):
        """Recursive helper for set, takes the current level, the desired value,
        and the future path"""
        # base case: no more path, set value and return current dictionary
        if len(args) <= 1:
            data[args[0]] = value
            return data
        # recursive call, call self while moving further down the path
        data[args[0]] = self.setHelper(data[args[0]], value, *args[1:])
        return data

    def get(self, *args):
        """This is the global getter, given a path, it will return the value"""
        data = self.data
        for arg in args:
            if arg not in data.keys():
                raise Exception(f"Getter called with {args}, but {arg} not found in {data.keys()}")
            data = data[arg]
        return data

    def notifyOberservers(self, key=None):
        """To notify all the observers, each one has a refreshView, that function is called,
        the model is passed, and the key that was changed (if applicable) is passed"""
        for ob in self.data["observers"]:
            ob.refreshView(self.__instance, key)
