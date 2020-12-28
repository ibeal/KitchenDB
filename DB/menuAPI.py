from recipeCreator import *
from DB.AbstractAPI import *
from DB.database import *
from dailyMenu import *

class MenuAPI(AbstractAPI):
    def __init__(self, db):
        self.db = db
        self.db.createTable(name='menus', fields=menu.dataFields)

    def menuExists(self, menu=None, name=""):
        if rec:
            name = menu.name
        logger.debug(f'checking for menu: {name}')
        res = self.db.cur.execute(f"SELECT * FROM menus WHERE name='{name}'")
        return len(list(res)) > 0

    def menuLookup(self, name='', menu=None):
        if menu:
            name = menu.name
        logger.debug(f'checking for menu: {name}')
        res = self.db.cur.execute(f"SELECT * FROM menus WHERE name='{name}'")
        return menu(res[0])

    def deleteMenu(self, menu=None, name=""):
        if menu:
            name = menu.name
        logger.debug(f'deleting menu: {name}')
        res = self.db.cur.execute(f"DELETE FROM recipes WHERE name='{name}'")
        self.db.conn.commit()

    def search(self, query, sortby=None):
        logger.debug(f'searching db for {query}')
        query = database.db_clean(query)
        # res = self.db.cur.execute("SELECT * FROM recipes WHERE name LIKE '%'||?||'%'", (query,))
        command = f"SELECT * FROM menus WHERE name LIKE ?"
        if not sortby in ['None', None]:
            sortby = sortby.lower()
            sortby = sortby.replace(' ', '_')
            command += f' ORDER BY ?'
            # print(command)
            res = self.db.cur.execute(command, ('%'+query+'%',sortby))
        else:
            res = self.db.cur.execute(command, ('%'+query+'%',))
        # self.unpack(res)
        return [menu(i) for i in res]

    def saveMenu(self, menu, table = 'menus'):
        # self.db.createTable(table)
        if len(menu.name) <= 0:
                print('Error saving recipe to db, skipping...')
                return
        data = rec.guts()
        # logger.debug('executing: ' + query)
        self.db.cur.execute(f"insert into {table} values (?,?,?,?)", tuple(data.values()))
        self.db.conn.commit()
