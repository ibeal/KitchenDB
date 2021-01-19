import logging
# from containers.recipe import recipe
from containers.shoppingList  import shoppingList
logger = logging.getLogger('dailyMenu Log')

class dailyMenu:
    def __init__(self, date='', data=None):
        if data:
            self.edit(data)
        else:
            self.new(date)

    def new(self, date):
        self.date = date
        # self.name = date
        # if name:
        #     self.name = name
        self.shopping = shoppingList()
        self.data = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'other': []
        }

    def edit(self, data):
        if isinstance(data, dict):
            self.date = data['date']
            self.data = data['data']
            self.newShoppingList()

    def pack(self):
        ret = {}
        for k,v in self.data.items():
            ret[k] = [rec.getID() for rec in v]
        return {'date':self.date,
                'data':ret}

    def add_category(self, group):
        if group in self.data.keys():
            logger.debug('Tried adding category that already exists')
        else:
            self.data[group] = []

    def add(self, group, rec):
        if group.lower() in ['breakfast']:
            self.data['breakfast'].append(rec)
        elif group.lower() in ['lunch']:
            self.data['lunch'].append(rec)
        elif group.lower() in ['dinner']:
            self.data['dinner'].append(rec)
        elif group.lower() in ['misc', 'other']:
            self.data['other'].append(rec)
        elif group.lower() in self.data.keys():
            self.data[group.lower()].append(rec)
        else:
            logger.debug("group not supported")
            raise Exception(f"Unsupported group given {group}")
        self.updateShoppingList(rec)

    def remove(self, group, rec):
        if group.lower() in ['breakfast']:
            self.data['breakfast'].remove(rec)
        elif group.lower() in ['lunch']:
            self.data['lunch'].remove(rec)
        elif group.lower() in ['dinner']:
            self.data['dinner'].remove(rec)
        elif group.lower() in ['misc', 'other']:
            self.data['other'].remove(rec)
        elif group.lower() in self.data.keys():
            self.data[group.lower()].remove(rec)
        else:
            logger.debug(f"group not supported")
            raise Exception(f"Unsupported group given '{group}'")
        self.updateShoppingList(rec, remove=True)

    def newShoppingList(self):
        self.shopping = shoppingList()
        self.shopping.add_ingredients(*self.data.values())

    def updateShoppingList(self, data, remove=False):
        self.shopping.add_ingredients(data) if not remove else self.shopping.remove_ingredients(data)

    def get(self, key):
        return self.data[key]

    def getIngs(self):
        return self.shopping.ingredients
