from config import *
from recipeCreator import *
global dataFields

class database:
    def __init__(self):
        self.conn = sql.connect('KitchenDB')
        self.cur = self.conn.cursor()

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

    def search(self, query):
        res = self.cur.execute("SELECT * FROM recipes WHERE name LIKE '%'||?||'%'", (query,))
        return [i for i in res]

    def addNew(self):
        rec = recipe()
        self.cur.execute('drop table if exists recipes')
        self.saveRecipe(rec)
        # with open('recipe.yaml') as f:
        #     self.cur.execute('drop table if exists recipes')
        #     self.create_from_yaml(f)


    def saveRecipe(self, rec):
        table = 'recipes'
        # tabfields = 'name string, prep_time integer, cook_time integer, yield string, category string,\
        #   rating integer, ingredients string, directions string'
        tabfields = ''
        for v in dataFields:
            tabfields += f'{v}, '
        tabfields = tabfields[:-2]
        query = 'create table if not exists ' + table + ' (' + tabfields + ')'

        logger.debug('executing: ' + query)
        self.cur.execute(query)

        query = f'insert into {table} values ("{rec.name}", {rec.prep_time}, {rec.cook_time}, "{rec.yieldAmnt}", "{rec.category}", {rec.rating}, "{str(rec.ingredients)}", "{str(rec.directions)}")'
        logger.debug('executing: ' + query)
        self.cur.execute(query)
        self.conn.commit()



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
        query = 'create table if not exists ' + tab['tabname'] + ' (' + tab['tabfields'] + ')'
        logger.debug('executing: ' + query)
        self.cur.execute(query)

        name, prep_time, cook_time, yieldAmnt, category, rating, ingredients, directions = tab['fields']
        table = tab['tabname']
        query = f'insert into {table} values ("{name}", {prep_time}, {cook_time}, "{yieldAmnt}", "{category}", {rating}, "{ingredients}", "{directions}")'
        logger.debug('executing: ' + query)
        self.cur.execute(query)
        self.conn.commit()
