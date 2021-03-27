import logging
logger = logging.getLogger('shoppingList Log')
# from containers.recipe import *
import containers.recipe as rc

class shoppingList:
    def __init__(self):
        self.ingredients = []

    def __str__(self):
        s = ''
        for ing in self.ingredients:
            s += f' -- {ing[2]} of {ing[0]}\n'
        return s

    def add_ingredients(self, *args):
        # no args, just return
        if len(args) < 1:
            return
        for arg in args:
            # if the argument is a recipe add each ingredient from the recipe
            # print(recipe)
            if isinstance(arg, rc.recipe):
                for ing in arg.ingredients:
                    self.ingredients.append(ing)
            # if the argument is a list, recursive call on each item in the list
            if isinstance(arg, list):
                for item in arg:
                    self.add_ingredients(item)
            # if the argument is another shopping list, it can be directly added
            if isinstance(arg, shoppingList):
                self.ingredients.extend(arg.ingredients)

    def getIngs(self):
        return self.ingredients

    def remove_ingredients(self, *args):
        # no args, just return
        if len(args) < 1:
            return
        for arg in args:
            # if the argument is a recipe add each ingredient from the recipe
            if isinstance(arg, rc.recipe):
                for ing in arg.ingredients:
                    try:
                        self.ingredients.remove(ing)
                    except ValueError:
                        continue
            # if the argument is a list, recursive call on each item in the list
            if isinstance(arg, list):
                for item in arg:
                    self.add_ingredients(item)
            # if the argument is another shopping list, it can be directly added
            if isinstance(arg, shoppingList):
                for ing in arg.ingredients:
                    try:
                        self.ingredients.remove(ing)
                    except ValueError:
                        continue
