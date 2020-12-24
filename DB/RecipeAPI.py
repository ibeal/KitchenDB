from recipeCreator import *
from DB.AbstractAPI import *
from DB.database import *
import json

class RecipeAPI(AbstractAPI):
    def __init__(self, db):
        self.db = db
        self.db.createTable(name='recipes', fields=recipe.dataFields)
        self.db.register_adapter(list, self.adapt_list_to_JSON)
        self.db.register_converter("json", self.convert_JSON_to_list)

    def showAll(self):
        self.result('select * from recipes')

    def recipes(self, first=0, last=None, count=1):
        """A function that returns a custom number of rows from recipes
            Input: first - int, number of the first row, default: 0
                   last - int, number of the last row
                   count - int, number of rows to get, default: 1
                   NOTE: if last is specified, count is overwritten

            Output: array of recipe rows, with length of count"""
        if last:
            count = last - first
        res = self.db.cur.execute(f"SELECT * FROM recipes LIMIT {first}, {count}")
        return [recipe(i) for i in res]

    def recipeExists(self, rec=None, name="", source=""):
        """Accepts either a name and source, or a recipe in the first slot"""
        if rec:
            name = rec.title
            source = rec.source
        logger.debug(f'checking for {name} by {source}')
        res = self.db.cur.execute(f"SELECT * FROM recipes WHERE title='{name}' AND source='{source}'")
        return len(list(res)) > 0

    def recipeLookup(self, name='', source='', rec=None):
        """Accepts either a name and source, or a recipe in the third slot"""
        if rec:
            name = rec.title
            source = rec.source
        logger.debug(f'checking for {name} by {source}')
        res = self.db.cur.execute(f"SELECT * FROM recipes WHERE title='{name}' AND source='{source}'")
        return recipe(res[0])

    def deleteRecipe(self, rec=None, name="", source=""):
        """Accepts either a name and source, or a recipe in the first slot"""
        if rec:
            name = rec.title
            source = rec.source
        logger.debug(f'deleting recipe {name} by {source}')
        res = self.db.cur.execute(f"DELETE FROM recipes WHERE title='{name}' AND source='{source}'")
        self.db.conn.commit()

    def search(self, query, sortby=None):
        logger.debug(f'searching db for {query}')
        query = database.db_clean(query)
        # res = self.db.cur.execute("SELECT * FROM recipes WHERE name LIKE '%'||?||'%'", (query,))
        command = f"SELECT * FROM recipes WHERE title LIKE ?"
        if not sortby in ['None', None]:
            sortby = sortby.lower()
            sortby = sortby.replace(' ', '_')
            command += f' ORDER BY ?'
            # print(command)
            res = self.db.cur.execute(command, ('%'+query+'%',sortby))
        else:
            res = self.db.cur.execute(command, ('%'+query+'%',))
        self.unpack(res)
        return [recipe(i) for i in res]

    # def getColumns(self, table):
    #     logger.debug(f'DEPRECATED getColumns CALLED')
    #     res = self.db.cur.execute(f"SELECT * FROM {table}")
    #     return [info[0] for info in res.description]

    def addNew(self, rec):
        # rec = recipe()
        self.db.cur.execute('drop table if exists recipes')
        self.saveRecipe(rec)

    def saveRecipe(self, rec, table = 'recipes'):
        # self.db.createTable(table)
        if len(rec.title) <= 0:
                print('Error saving recipe to db, skipping...')
                return
        # print(database.db_clean(rec.directions))
        # for dir in database.db_clean(rec.directions):
        #     print(dir)
        query = f'insert into {table} values ("{rec.title}", {rec.prep_time}, {rec.cook_time}, "{rec.yieldAmnt}", "{rec.category}", {rec.rating}, "{str(database.db_clean(rec.ingredients))}", "{str(database.db_clean(rec.directions))}", "{rec.source}")'
        logger.debug('executing: ' + query)
        self.db.cur.execute(query)
        self.db.conn.commit()

    def adapt_list_to_JSON(lst):
        return json.dumps(lst).encode('utf8')

    def convert_JSON_to_list(data):
        return json.loads(data.decode('utf8'))
