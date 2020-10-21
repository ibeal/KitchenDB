from recipeCreator import *
import logging
logger = logging.getLogger('Debug Log')

class database:
    APOSREPLACE = ';:'
    findApos = re.compile("'")
    fillApos = re.compile(APOSREPLACE)
    def __init__(self, returnRecipe=True, source='KitchenDB'):
        self.conn = sql.connect(source)
        self.cur = self.conn.cursor()
        self.returnRecipe = returnRecipe
        self.createTable()

    def __del__(self):
        self.conn.close()

    def result(self, query):
        """A function that displays the result of a query"""
        res = self.cur.execute(query)            # Execute query
        for fieldinfo in res.description:
            print(fieldinfo[0])     # Print column names
        print()
        for row in res:                     # Print rows
            print(row)
        print()

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
        res = self.cur.execute(f"SELECT * FROM recipes LIMIT {first}, {count}")
        if self.returnRecipe:
            return [recipe(i) for i in res]
        return [i for i in res]

    def recipeExists(self, name, source=""):
        if isinstance(name, recipe):
            name = name.title
        logger.debug(f'checking for {name}')
        res = self.cur.execute(f"SELECT * FROM recipes WHERE title='{name}'")
        return len(list(res)) > 0

    def deleteRecipe(self, name):
        if isinstance(name, recipe):
            name = name.title
        logger.debug(f'deleting recipe {name}')
        res = self.cur.execute(f"DELETE FROM recipes WHERE title='{name}'")
        self.conn.commit()

    def search(self, query, sortby=None):
        logger.debug(f'searching db for {query}')
        # res = self.cur.execute("SELECT * FROM recipes WHERE name LIKE '%'||?||'%'", (query,))
        command = f"SELECT * FROM recipes WHERE title LIKE '%'||?||'%'"
        if sortby:
            command += f' ORDER BY ?'
            res = self.cur.execute(command, (query,sortby))
        else:
            res = self.cur.execute(command, (query,))

        if self.returnRecipe:
            return [recipe(i) for i in res]
        return [i for i in res]

    def getColumns(self, table):
        logger.debug(f'DEPRECATED getColumns CALLED')
        res = self.cur.execute(f"SELECT * FROM {table}")
        return [info[0] for info in res.description]

    def addNew(self, rec):
        rec = recipe()
        self.cur.execute('drop table if exists recipes')
        self.saveRecipe(rec)
        # with open('recipe.yaml') as f:
        #     self.cur.execute('drop table if exists recipes')
        #     self.create_from_yaml(f)


    def createTable(self, table = 'recipes'):
        # tabfields = 'name string, prep_time integer, cook_time integer, yield string, category string,\
        #   rating integer, ingredients string, directions string'
        # self.cur.execute('drop table ' + table)
        tabfields = ''
        for v in recipe.dataFields:
            tabfields += f'{v}, '
        tabfields = tabfields[:-2]
        query = 'create table if not exists ' + table + ' (' + tabfields + ')'

        logger.debug('executing: ' + query)
        self.cur.execute(query)
        self.conn.commit()

    def saveRecipe(self, rec, table = 'recipes'):
        self.createTable(table)
        if len(rec.title) <= 0:
                print('Error saving recipe to db, skipping...')
                return
        query = f'insert into {table} values ("{rec.title}", {rec.prep_time}, {rec.cook_time}, "{rec.yieldAmnt}", "{rec.category}", {rec.rating}, "{str(database.aposFilter(rec.ingredients))}", "{str(database.aposFilter(rec.directions))}", "{rec.source}")'
        logger.debug('executing: ' + query)
        self.cur.execute(query)
        self.conn.commit()

    def pack(rec):
        # TODO: figure out these conversions
        ing = "{str(database.aposFilter(rec.ingredients))}"
        dirs = "{str(database.aposFilter(rec.directions))}"
        return tuple(rec.title, rec.prep_time, rec.cook_time, rec.yieldAmnt, rec.category, rec.rating, ing, dirs, rec.source)

    @staticmethod
    def aposFilter(dirty):
        """A function that takes a string and replaces all apostrophes with the global
        APOSREPLACE value, currently ';:'. Inverse of aposFiller."""
        if not isinstance(dirty, str):
            logger.debug(f'{dirty} is not a string. aposFilter aborting...')
            return dirty
        clean = database.findApos.sub(database.APOSREPLACE, dirty)
        return clean

    @staticmethod
    def aposFiller(clean):
        """A function that takes a string and replaces all instances of COMMAREPLACE,
        currently ';:', with an apostrophe. Inverse of aposFilter."""
        if not isinstance(clean, str):
            logger.debug(f'{clean} is not a string. aposFiller aborting...')
            return clean
        dirty = database.fillApos.sub("'", clean)
        return dirty

    def create_from_csv(self, f):
        """A function that creates tables from csv files"""
        tabname = f.readline()[:-1]
        fieldspec = f.readline()[:-1]
        query = 'create table if not exists ' + tabname + ' (' + fieldspec + ')'
        logger.debug(query)
        self.cur.execute(query)
        for row in csv.reader(f):
            query = 'insert into ' + tabname + ' values' + str(tuple(row))  # csv returns a list, hence tuple(row)
            logger.debug(query)
            self.cur.execute(query)
        self.conn.commit()

    def create_from_yaml(self, f):
        """A function that creates tables from yaml files"""
        tab = yaml.load(f,Loader=yaml.FullLoader)
        # query = 'create table if not exists ' + tab['tabname'] + ' (' + tab['tabfields'] + ')'
        # logger.debug('executing: ' + query)
        # self.cur.execute(query)

        title, prep_time, cook_time, yieldAmnt, category, rating, ingredients, directions, source = tab['fields']
        table = tab['tabname']
        query = f'insert into {table} values ("{title}", {prep_time}, {cook_time}, "{yieldAmnt}", "{category}", {rating}, "{ingredients}", "{directions}", "{source}")'
        logger.debug('executing: ' + query)
        self.cur.execute(query)
        self.conn.commit()

if __name__ == '__main__':
    # Testing
    db = database()
