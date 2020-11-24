import dailyMenu

class menu:
    def __init__(self):
        self.shoppingList = []
        self.menus = {}
        self.start_date = self.menus.keys()[0]
        self.end_date = self.menus.keys()[-1]

    def addRecipe(self, rec, date):
        self.menus[date].addRecipe(rec)

    def updateShoppingList(self):
        newShopping = []
        for menu in self.menus:
            newShopping.append(menu.recipes)
