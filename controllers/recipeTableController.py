import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
import KitchenGUI.searchBar as search
from database import *
from recipeCreator import *
from apiCalls import *
from KitchenModel import *
from controllers.controller import controller
logger = logging.getLogger('Debug Log')

class recipeTableController(controller):
    def __init__(self, tableKey, features, recTable, tableData, recTableDim):
        self.tableKey = tableKey
        self.model = KitchenModel.getInstance()
        self.features = features
        self.recTable = recTable
        self.tableData = tableData
        self.recTableDim = recTableDim

    def handle(self, event, values):
        if event == self.tableKey:
            # click on table, event to be handled by main
            # self.master.switchTabs('-EDITOR-')
            # self.master.deferHandle('-EDITOR-', 'fill', values)
            return False
        elif event == '-RECIPE-SBUTTON-':
            self.searchdb(values['-RECIPE-SBOX-'], sortby=values['-TABLE-SORT-'])
            return True
        return False

    def searchdb(self, query, sortby):
        # row, col = self.recTableDim
        # get search results
        recs = self.model.get('db').search(query) if sortby == 'None' else self.model.get('db').search(query, sortby)
        data = []
        for rec in recs:
            recInfo = rec.guts()
            temp = []
            for col in self.features:
                temp.append(recInfo[col])
            data.append(temp)

        # preppend header list
        # data = [header, *data]
        # pass all data to update table
        self.model.setState("lastTableAction", "search")
        self.model.setState("lastSearch", query)
        self.tableData = recs
        self.recTable.update(values = data)

    def refreshRecipeTable(self):
        logger.debug("Refreshing recipe table")
        row, col = self.recTableDim
        if self.model.getState("lastTableAction") == "default":
            logger.debug("last state was default")
            recs = self.model.get('db').recipes(count=row)
        elif self.model.getState("lastTableAction") == "search":
            logger.debug("last state was search")
            recs = self.model.get('db').search(self.model.getState("lastSearch"))
        # create data matrix
        data = []
        for rec in recs:
            recInfo = rec.guts()
            temp = []
            for col in self.features:
                temp.append(recInfo[col])
            data.append(temp)

        # preppend header list
        # data = [header, *data]
        self.tableData = recs
        # chop off ing and dirs for display
        self.recTable.update(values=data)
