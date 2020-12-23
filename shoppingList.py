import logging
logger = logging.getLogger('shoppingList Log')
from recipeCreator import *

class shoppingList:
    def __init__(self):
        self.ingredients = []

    def add_ingredients(self, *args):
        # no args, just return
        if len(args) < 1:
            return
        for arg in args:
            # if the argument is a recipe add each ingredient from the recipe
            if isinstance(arg, recipe):
                for ing in arg.ingredients:
                    self.ingredients.append(ing)
            # if the argument is a list, recursive call on each item in the list
            if isinstance(arg, list):
                for item in arg:
                    self.add_ingredients(item)
            # if the argument is another shopping list, it can be directly added
            if isinstance(arg, shoppingList):
                self.ingredients.extend(arg.ingredients)
