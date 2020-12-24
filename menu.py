from dailyMenu import *
import datetime
import pandas as pd
from shoppingList import *

class menu:
    dataFields = ['name string', 'startDate string', 'endDate string',\
      'ingredients list', 'directions list', 'source string']
    def __init__(self, start=None, end=None, name=None):
        self.name = name
        self.shopping = shoppingList()
        self.menus = {}
        self.start_date = datetime.date.fromisoformat(start) if start else None
        self.end_date = datetime.date.fromisoformat(end) if end else None
        if self.start_date and self.end_date and len(self.menus) == 0:
            self.create_menus()

    def startDate(self, start):
        self.start_date = datetime.date.fromisoformat(start)
        if self.start_date and self.end_date and len(self.menus) == 0:
            self.create_menus()

    def endDate(self, end):
        self.end_date = datetime.date.fromisoformat(end)
        if self.start_date and self.end_date and len(self.menus) == 0:
            self.create_menus()

    def create_menus(self):
        if None in [self.start_date, self.end_date]:
            raise Exception(f"tried to create menus while missing {'start' if not self.start_date else 'end'} date")
        for date in pd.date_range(start=self.start_date, end=self.end_date).to_pydatetime().tolist():
            self.menus[date.date().isoformat()] = dailyMenu(date.date().isoformat())

    def addRecipe(self, rec, date, group):
        self.menus[date].add(group, rec)

    def updateShoppingList(self, data):
        self.shopping.add(data)
