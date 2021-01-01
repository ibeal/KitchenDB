import logging
from containers.recipe import *
from containers.menu import *
from containers.dailyMenu import *
from containers.shoppingList import *
logger = logging.getLogger('nutrition object Log')

class nutrition:
    def __init__(self, data=None):
        self.ingredients = []
        if data:
            self.edit(data)
        else:
            self.new()

    def edit(self, data):
        if isinstance(data, list):
            for item in data:
                self.edit(item)
        elif isinstance(data, data_container):
            self.ingredients.extend(data.getIngs())
        elif isinstance(data, dailyMenu):
            self.ingredients.extend(data.getIngs())
        else:
            self.ingredients.append(data)

    def new(self):
        self.ingredients = []
