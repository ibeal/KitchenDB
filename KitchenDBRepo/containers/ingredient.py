import logging
import json
import copy
from containers.convert import convert
logger = logging.getLogger('ingredient object Log')

class ingredient:
    unit_aliases = {
        'Cups': [
            'cup',
            'cups',
            'c'
        ], 
        'tsp': [
            'tsp',
            'tsps',
            't'
        ], 
        'Tbsp': [
            'tbsp',
            'tbsps',
            # This case has to be covered before the for loop
            'T'
        ]}
    units = ['Cups', 'tsp', 'Tbsp']
    def __init__(self, data=None):
        if isinstance(data, ingredient):
            self.copyfrom(copy.deepcopy(data))
        elif data:
            self.edit(data)
        else:
            self.new()

    def copyfrom(self, data):
        self.name = data.name
        self.id = data.id
        self.amount = data.amount
        self.unit = data.unit

    def edit(self, data):
        if isinstance(data, dict):
            self.name = data["name"]
            self.id = data["id"]
            self.amount = data["amount"]
            self.unit = data["unit"]
        elif isinstance(data, list) or isinstance(data, tuple):
            # backward compatibility
            if len(data) == 3:
                self.name = data[0]
                self.id = data[1]
                self.amount = data[2].split(" ")[0]
                self.unit = ' '.join(data[2].split(" ")[1:])
                return
            self.name = data[0]
            self.id = data[1]
            self.amount = data[2]
            self.unit = data[3]
        elif isinstance(data, str):
            print(data)
            print(json.loads(data))
            self.edit(json.loads(data))
        else:
            logger.debug('Unknown datatype recieved')
            raise Exception(f'ingredient got data that wasnt expected. type recieved was {type(data)}')

    def new(self):
        self.name = None
        self.id = None
        self.amount = None
        self.unit = ingredient.units[0]
        self.servings = None

    def update_amount(self, amount=None, unit=None):
        if amount:
            self.amount = amount
        if unit:
            self.unit = unit
            
    def guts(self):
        return {
            "name":self.name,
            "id":self.id,
            "amount":self.amount,
            "unit":self.unit
        }

    def __str__(self):
        # return f"{self.amount} {self.unit} of {self.name}(id:{self.id})"
        return f"{self.amount} {self.unit} of {self.name}"

    def pack(self):
        return self.guts()

    @staticmethod
    def standardize_unit(target):
        if target == 'T':
            return 'Tbsp'
        target = target.lower()
        for unit, aliases in ingredient.unit_aliases:
            if target in aliases:
                return unit
