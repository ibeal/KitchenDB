class menu:
    def __init__(self):
        self.shoppingList = []
        self.recipes = {'Breakfast':[], 'Lunch':[], 'Dinner':[], 'Snacks':[]

    def addRecipe(self, rec, group):
        self.recipes[group].append(rec)
