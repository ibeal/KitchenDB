

class RecipeAPI:
    def __init__(self, db):
        self.db = db

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
    if self.returnRecipe:
        return [recipe(i) for i in res]
    return [i for i in res]

def recipeExists(self, name, source=""):
    if isinstance(name, recipe):
        name = name.title
    logger.debug(f'checking for {name}')
    res = self.db.cur.execute(f"SELECT * FROM recipes WHERE title='{name}'")
    return len(list(res)) > 0

def deleteRecipe(self, name):
    if isinstance(name, recipe):
        name = name.title
    logger.debug(f'deleting recipe {name}')
    res = self.db.cur.execute(f"DELETE FROM recipes WHERE title='{name}'")
    self.conn.commit()

def search(self, query, sortby=None):
    logger.debug(f'searching db for {query}')
    # res = self.db.cur.execute("SELECT * FROM recipes WHERE name LIKE '%'||?||'%'", (query,))
    command = f"SELECT * FROM recipes WHERE title LIKE ?"
    if not sortby in ['None', None]:
        sortby = sortby.lower()
        sortby = sortby.replace(' ', '_')
        command += f' ORDER BY ?'
        print(command)
        res = self.db.cur.execute(command, ('%'+query+'%',sortby))
    else:
        res = self.db.cur.execute(command, ('%'+query+'%',))

    if self.returnRecipe:
        return [recipe(i) for i in res]
    return [i for i in res]

def getColumns(self, table):
    logger.debug(f'DEPRECATED getColumns CALLED')
    res = self.db.cur.execute(f"SELECT * FROM {table}")
    return [info[0] for info in res.description]

def addNew(self, rec):
    # rec = recipe()
    self.db.cur.execute('drop table if exists recipes')
    self.saveRecipe(rec)
