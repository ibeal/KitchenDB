from dailyMenu import *
import datetime
import pandas as pd
from shoppingList import *
from data_container import *

class menu(data_container):
    dataFields = ['name string', 'startDate string', 'endDate string', 'menus json']
    ugly_fields = ['name', 'startDate', 'endDate', 'menus']
    pretty_fields = ['Name', 'Start Date', 'End Date', 'Menus']
    date_delimiter = ':'
    def __init__(self, data=None, copyme=None, readIn=None, start=None, end=None, name=None):
        if copyme:
            self.edit(copy.deepcopy(copyme).guts())
        elif data:
            self.edit(data)
        elif readIn:
            self.readIn(readIn)
        else:
            self.new(start, end, name)

    def new(self, start, end, name):
        self.shopping = shoppingList()
        self.menus = {}
        self.start_date = datetime.date.fromisoformat(start) if start else None
        self.end_date = datetime.date.fromisoformat(end) if end else None
        if name in ['', None]:
            self.name = f'{self.start_date.isoformat()}{menu.date_delimiter}{self.end_date.isoformat()}'
        else:
            self.name = name
        if self.start_date and self.end_date and len(self.menus) == 0:
            self.create_menus()

    def edit(self, data):
        if isinstance(data, list) or isinstance(data, tuple):
            self.name = data[0]
            if len(self.title) <= 0:
                print('Error creating recipe, creating default')
                self.new()
                return
            self.start_date = data[1]
            self.end_date = data[2]
            self.menus = data[3]
        elif isinstance(data, dict):
            self.menus = data['name']
            if len(self.title) <= 0:
                print('Error creating recipe, creating default')
                self.new()
                return
            self.start_date = data['startDate']
            self.end_date = data['endDate']
            self.menus = data['menus']

    def readIn(self, file):
        pass

    # def startDate(self, start):
    #     """set startdate and initialize menus if end date is present"""
    #     self.start_date = datetime.date.fromisoformat(start)
    #     if self.start_date and self.end_date and len(self.menus) == 0:
    #         self.create_menus()
    #
    # def endDate(self, end):
    #     """set end date and initialize menus if start date is present"""
    #     self.end_date = datetime.date.fromisoformat(end)
    #     if self.start_date and self.end_date and len(self.menus) == 0:
    #         self.create_menus()

    def create_menus(self):
        """creates a day for each day between start and end dates"""
        if None in [self.start_date, self.end_date]:
            raise Exception(f"tried to create menus while missing {'start' if not self.start_date else 'end'} date")
        for date in pd.date_range(start=self.start_date, end=self.end_date).to_pydatetime().tolist():
            self.menus[date.date().isoformat()] = dailyMenu(date.date().isoformat())

    def addRecipe(self, rec, date, group):
        """adds a recipe to the specified day's group"""
        self.menus[date].add(group, rec)

    def updateShoppingList(self, data):
        """add the data to the shopping list, used to keep the shopping list up
        to date"""
        self.shopping.add(data)

    def getDay(self, day):
        """returns a given day, if an int is given, it will return that many days
        after the start date. otherwise, it returns the date from the given string"""
        if isinstance(day, int):
            day = self.start_date + datetime.timedelta(days=day)
        if isinstance(day, datetime.date):
            day = day.isoformat()
        return self.menus[day]

    def guts(self):
        return {"name": self.name,
                "startDate": self.startDate,
                "endDate": self.endDate,
                "menus": self.menus}

    def getID(self):
        return self.name

    def getName(self):
        return self.name
