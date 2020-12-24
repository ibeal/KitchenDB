from recipeCreator import *
from DB.AbstractAPI import *
from DB.database import *
from dailyMenu import *

class RecipeAPI(AbstractAPI):
    def __init__(self, db):
        self.db = db
        self.db.createTable(name='menus', fields=menu.dataFields)

    
