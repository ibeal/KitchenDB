import logging
from containers.recipe  import recipe
from DB.AbstractAPI import AbstractAPI
from DB.database import database
from containers.dailyMenu import dailyMenu
from containers.menu import menu as Menu
logger = logging.getLogger("MenuAPI Log")

class MenuAPI(AbstractAPI):
    def __init__(self, db, recipeAPI):
        self.recAPI = recipeAPI
        self.db = db
        self.db.createTable(name='menus', fields=Menu.dataFields)

    def exists(self, menu=None, name=""):
        if menu:
            name = menu.name
        logger.debug(f'checking for menu: {name}')
        res = self.db.cur.execute(f"SELECT * FROM menus WHERE name='{name}'")
        return len(list(res)) > 0

    def lookup(self, name='', menu=None):
        if menu:
            name = menu.name
        logger.debug(f'checking for menu: {name}')
        res = self.db.cur.execute(f"SELECT * FROM menus WHERE name='{name}'")
        ret = Menu(list(res)[0])
        ret = self.menuUnpack(ret)
        return ret

    def menuUnpack(self, menu):
        ret = menu
        for k,v in ret.menus.items():
            # iterate over categories...
            for key,val in v['data'].items():
                # iterate over recipes in categories...
                # and use the recipeID to lookup the recipe in the database
                holder = []
                # TODO: add error checking for missing recipe
                for rec in val:
                    temp_rec = self.recAPI.lookup(recID=rec)
                    if temp_rec is None:
                        temp_rec = self.recAPI.lookup(name=rec.split(recipe.id_delimiter)[0], source=None)
                    if temp_rec is None:
                        ret.missing_recipes.append(rec)
                        continue
                    holder.append(temp_rec)

                v['data'][key] = holder
            # then update the menu with the new dailyMenu object
            ret.setDay(dailyMenu(data=v))
        return ret

    def delete(self, menu=None, name=""):
        if menu:
            name = menu.name
        logger.debug(f'deleting menu: {name}')
        res = self.db.cur.execute(f"DELETE FROM menus WHERE name='{name}'")
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
        # TODO: add unpacking logic here
        return [Menu(data=i) for i in res]

    def save(self, menu, table = 'menus'):
        # self.db.createTable(table)
        if len(menu.name) <= 0:
                print('Error saving recipe to db, skipping...')
                return
        menu = menu.pack()
        data = menu.guts()
        # logger.debug('executing: ' + query)
        self.db.cur.execute(f"insert into {table} values (?,?,?,?)", tuple(data.values()))
        self.db.conn.commit()
