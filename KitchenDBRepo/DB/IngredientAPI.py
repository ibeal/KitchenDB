import logging
from DB.AbstractAPI import AbstractAPI
from DB.database import database
logger = logging.getLogger('IngredientAPI Log')

class IngredientAPI(AbstractAPI):
    def __init__(self, db):
        self.db = db
        self.db.createTable(name='ingredients', fields=['id int', 'name string', 'data json'])

    def search(self, query):
        res = self.db.cur.execute(
            f"SELECT * from ingredients WHERE name LIKE {query}")


    def exists(self, key):
        res = self.db.cur.execute(
            f"SELECT * from ingredients WHERE id='{key}'")
        return bool(len(res) > 0)

    def lookup(self, key):
        res = self.db.cur.execute(f"SELECT * from ingredients WHERE id='{key}'")
        return res

    def delete(self, key):
        self.db.cur.execute(f"DELETE from ingredients where id='{key}'")
        self.db.conn.commit()

    def save(self, item):
        id_num = item['fdcId']
        name = item['description']
        self.db.cur.execute(f"INSERT into ingredients values ({id_num},{name},{item})")
        self.db.conn.commit()
