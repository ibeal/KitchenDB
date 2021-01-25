import json
import logging
from containers.recipe import recipe
from DB.AbstractAPI import AbstractAPI
from DB.database import database
logger = logging.getLogger('RecipeAPI Log')

class RecipeAPI(AbstractAPI):
    def __init__(self, db):
        self.db = db
        # self.db.dropTable('recipes')
        self.db.createTable(name='recipes', fields=recipe.dataFields)


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

    def exists(self, rec=None, name="", source="", recID=None):
        """Accepts either a name and source, or a recipe in the first slot"""
        if rec:
            name = rec.title
            source = rec.source
        elif recID:
            fields = recID.split(recipe.id_delimiter)
            name = fields[0]
            source = fields[1] if len(fields) > 1 else ''
        logger.debug(f'checking for {name} by {source}')
        # if None is passed, then perform a lookup by title only
        if source == None:
            res = self.db.cur.execute(f"SELECT * FROM recipes WHERE title='{name}'")
        else:
            res = self.db.cur.execute(f"SELECT * FROM recipes WHERE title='{name}' AND source='{source}'")
        return len(list(res)) > 0

    def lookup(self, name='', source='', rec=None, recID=None):
        """Accepts either a name and source, or a recipe in the third slot"""
        if rec:
            name = rec.title
            source = rec.source
        elif recID:
            fields = recID.split(recipe.id_delimiter)
            name = fields[0]
            source = fields[1] if len(fields) > 1 else ''
        logger.debug(f'checking for {name} by {source}')
        if source == None:
            res = list(self.db.cur.execute(f"SELECT * FROM recipes WHERE title='{name}'"))
        else:
            res = list(self.db.cur.execute(f"SELECT * FROM recipes WHERE title='{name}' AND source='{source}'"))
        return recipe(res[0]) if len(res) > 0 else None

    def delete(self, rec=None, name="", source=""):
        """Accepts either a name and source, or a recipe in the first slot"""
        if isinstance(rec, recipe):
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
        # self.unpack(res)
        return [recipe(i) for i in res]

    # def getColumns(self, table):
    #     logger.debug(f'DEPRECATED getColumns CALLED')
    #     res = self.db.cur.execute(f"SELECT * FROM {table}")
    #     return [info[0] for info in res.description]

    def addNew(self, rec):
        # rec = recipe()
        self.db.cur.execute('drop table if exists recipes')
        self.save(rec)

    def save(self, rec, table = 'recipes'):
        # self.db.createTable(table)
        if len(rec.title) <= 0:
                print('Error saving recipe to db, skipping...')
                return
        # print(database.db_clean(rec.directions))
        # for dir in database.db_clean(rec.directions):
        #     print(dir)
        # query = f'insert into {table} values ("{rec.title}", {rec.prep_time}, {rec.cook_time}, "{rec.yieldAmnt}", "{rec.category}", {rec.rating}, "{str(database.db_clean(rec.ingredients))}", "{str(database.db_clean(rec.directions))}", "{rec.source}")'
        # self.db.cur.execute(query)
        data = rec.guts()
        data.pop('Total Time')
        # print(tuple(data.values()))
        # logger.debug('executing: ' + query)
        self.db.cur.execute(f"insert into {table} values (?,?,?,?,?,?,?,?,?)", tuple(data.values()))
        self.db.conn.commit()
