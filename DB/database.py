from recipeCreator import *
import logging
logger = logging.getLogger('Debug Log')

class database:
    APOSREPLACE = ';:'
    findApos = re.compile("'")
    fillApos = re.compile(APOSREPLACE)

    PARENREPLACE = '^<'
    findParen = re.compile('"')
    fillParen = re.compile(PARENREPLACE)
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

    # def showAll(self):
    #     self.result('select * from recipes')
    #
    # def recipes(self, first=0, last=None, count=1):
    #     """A function that returns a custom number of rows from recipes
    #         Input: first - int, number of the first row, default: 0
    #                last - int, number of the last row
    #                count - int, number of rows to get, default: 1
    #                NOTE: if last is specified, count is overwritten
    #
    #         Output: array of recipe rows, with length of count"""
    #     if last:
    #         count = last - first
    #     res = self.cur.execute(f"SELECT * FROM recipes LIMIT {first}, {count}")
    #     if self.returnRecipe:
    #         return [recipe(i) for i in res]
    #     return [i for i in res]
    #
    # def recipeExists(self, name, source=""):
    #     if isinstance(name, recipe):
    #         name = name.title
    #     logger.debug(f'checking for {name}')
    #     res = self.cur.execute(f"SELECT * FROM recipes WHERE title='{name}'")
    #     return len(list(res)) > 0
    #
    # def deleteRecipe(self, name):
    #     if isinstance(name, recipe):
    #         name = name.title
    #     logger.debug(f'deleting recipe {name}')
    #     res = self.cur.execute(f"DELETE FROM recipes WHERE title='{name}'")
    #     self.conn.commit()
    #
    # def search(self, query, sortby=None):
    #     logger.debug(f'searching db for {query}')
    #     # res = self.cur.execute("SELECT * FROM recipes WHERE name LIKE '%'||?||'%'", (query,))
    #     command = f"SELECT * FROM recipes WHERE title LIKE ?"
    #     if not sortby in ['None', None]:
    #         sortby = sortby.lower()
    #         sortby = sortby.replace(' ', '_')
    #         command += f' ORDER BY ?'
    #         print(command)
    #         res = self.cur.execute(command, ('%'+query+'%',sortby))
    #     else:
    #         res = self.cur.execute(command, ('%'+query+'%',))
    #
    #     if self.returnRecipe:
    #         return [recipe(i) for i in res]
    #     return [i for i in res]

    def getColumns(self, table):
        logger.debug(f'DEPRECATED getColumns CALLED')
        res = self.cur.execute(f"SELECT * FROM {table}")
        return [info[0] for info in res.description]

    # def addNew(self, rec):
    #     rec = recipe()
    #     self.cur.execute('drop table if exists recipes')
    #     self.saveRecipe(rec)
    #     # with open('recipe.yaml') as f:
    #     #     self.cur.execute('drop table if exists recipes')
    #     #     self.create_from_yaml(f)


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

    # def saveRecipe(self, rec, table = 'recipes'):
    #     self.createTable(table)
    #     if len(rec.title) <= 0:
    #             print('Error saving recipe to db, skipping...')
    #             return
    #     query = f'insert into {table} values ("{rec.title}", {rec.prep_time}, {rec.cook_time}, "{rec.yieldAmnt}", "{rec.category}", {rec.rating}, "{str(database.db_clean(rec.ingredients))}", "{str(database.db_clean(rec.directions))}", "{rec.source}")'
    #     logger.debug('executing: ' + query)
    #     self.cur.execute(query)
    #     self.conn.commit()

    def pack(rec):
        # TODO: figure out these conversions
        ing = "{str(database.db_clean(rec.ingredients))}"
        dirs = "{str(database.db_clean(rec.directions))}"
        return tuple(rec.title, rec.prep_time, rec.cook_time, rec.yieldAmnt, rec.category, rec.rating, ing, dirs, rec.source)

    @staticmethod
    def aposFilter(dirty):
        """A function that takes a string and replaces all apostrophes with the global
        APOSREPLACE value, currently ';:'. Inverse of aposFiller."""
        logger.debug(f'aposFilter called with {dirty} of type {type(dirty)}')
        if isinstance(dirty, str):
            clean = database.findApos.sub(database.APOSREPLACE, dirty)
            return clean
        elif isinstance(dirty, list):
            return [database.aposFilter(dirt) for dirt in dirty]
        elif isinstance(dirty, dict):
            return {(key,database.aposFilter(dirt)) for key,dirt in dirty}
        logger.debug(f'{dirty} is not a string. aposFilter aborting...')
        return dirty

    @staticmethod
    def aposFiller(clean):
        """A function that takes a string and replaces all instances of COMMAREPLACE,
        currently ';:', with an apostrophe. Inverse of aposFilter."""
        logger.debug(f'aposFiller called with {clean} of type {type(clean)}')
        if isinstance(clean, str):
            dirty = database.fillApos.sub("'", clean)
            return dirty
        elif isinstance(clean, list):
            return [database.aposFiller(cleanee) for cleanee in clean]
        elif isinstance(clean, dict):
            return {(key,database.aposFiller(cleanee)) for key,cleanee in clean}
        logger.debug(f'{clean} is not a string. aposFiller aborting...')
        return clean

    @staticmethod
    def parenFilter(dirty):
        """A function that takes a string and replaces all parenthesis with the global
        PARENREPLACE value, currently '?*'. Inverse of parenFiller."""
        logger.debug(f'parenFilter called with {dirty} of type {type(dirty)}')
        if isinstance(dirty, str):
            clean = database.findParen.sub(database.PARENREPLACE, dirty)
            return clean
        elif isinstance(dirty, list):
            return [database.parenFilter(dirt) for dirt in dirty]
        elif isinstance(dirty, dict):
            return {(key,database.parenFilter(dirt)) for key,dirt in dirty}
        logger.debug(f'{dirty} is not a string. parenFilter aborting...')
        return dirty

    @staticmethod
    def parenFiller(clean):
        """A function that takes a string and replaces all instances of PARENREPLACE,
        currently ';:', with an parenthesis. Inverse of parenFilter."""
        logger.debug(f'parenFiller called with {clean} of type {type(clean)}')

        if isinstance(clean, str):
            dirty = database.fillParen.sub('"', clean)
            return dirty
        elif isinstance(clean, list):
            return [database.parenFiller(cleanee) for cleanee in clean]
        elif isinstance(clean, dict):
            return {(key,database.parenFiller(cleanee)) for key,cleanee in clean}
        logger.debug(f'{clean} is not a string. parenFiller aborting...')
        return clean

    @staticmethod
    def db_clean(dirty):
        cleanish = database.aposFilter(dirty)
        clean = database.parenFilter(cleanish)
        return clean

    @staticmethod
    def db_dirt(clean):
        dirt = database.aposFiller(clean)
        dirty = database.parenFiller(dirt)
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
