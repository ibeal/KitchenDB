import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
import KitchenGUI.searchBar as search
from DB.database import *
from recipeCreator import *
from apiCalls import *
from KitchenModel import *
from controllers.controller import controller
logger = logging.getLogger('recipeTableController Log')

class recipeTableController(controller):
    def __init__(self):
        self.model = KitchenModel.getInstance()

    def setup(self):
        logger.debug("setup initiated...")
        self.features = self.model.get("tabData", "-TABLE-", "features")
        self.recTable = self.model.get("tabData", "-TABLE-", "recTable")
        self.tableData = self.model.get("tabData", "-TABLE-", "tableData")
        self.recTableDim = self.model.get("tabData", "-TABLE-", "recTableDim")
        self.tableKey = self.model.get("tabData", "-TABLE-", "tableKey")

    def handle(self, event, values):
        if event == self.tableKey:
            # click on table, event to be handled by main
            # self.master.switchTabs('-EDITOR-')
            # self.master.deferHandle('-EDITOR-', 'fill', values)
            # self.model.get('views', ('-VIEWER-').Select()
            self.model.set('active_view', value='-VIEWER-')
            self.model.set('activeRecipe', value=self.model.get("tabData", "-TABLE-", "tableData")[values['-RECIPE-TABLE-'][0]])
            return True
        elif event == '-RECIPE-SBUTTON-':
            self.searchdb(values['-RECIPE-SBOX-'], sortby=values['-TABLE-SORT-'])
            return True
        elif event == '-ADDNEW-':
            self.model.set('activeRecipe', value=None)
            self.model.set('active_view', value='-EDITOR-')
            return True
        return False

    def searchdb(self, query, sortby):
        # row, col = self.recTableDim
        # get search results
        recs = self.model.get('RecipeAPI').search(query) if sortby == 'None' else self.model.get('RecipeAPI').search(query, sortby)
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
        self.model.set("state", "lastTableAction", value="search", notify=False)
        self.model.set("state", "lastSearch", value=query, notify=False)
        self.tableData = recs
        self.recTable.update(values = data)
        self.model.set("tabData", "recTable", value=self.recTable)

    # def refreshRecipeTable(self):
    #     logger.debug("Refreshing recipe table")
    #     row, col = self.recTableDim
    #     if self.model.get("state", "lastTableAction") == "default":
    #         logger.debug("last state was default")
    #         recs = self.model.get('RecipeAPI').recipes(count=row)
    #     elif self.model.get("state", "lastTableAction") == "search":
    #         logger.debug("last state was search")
    #         recs = self.model.get('RecipeAPI').search(self.model.get("state", "lastSearch"))
    #     else:
    #         raise Exception("Unknown last state!")
    #     # create data matrix
    #     data = []
    #     for rec in recs:
    #         recInfo = rec.guts()
    #         temp = []
    #         for col in self.features:
    #             temp.append(recInfo[col])
    #         data.append(temp)
    #
    #     # preppend header list
    #     # data = [header, *data]
    #     self.tableData = recs
    #     # chop off ing and dirs for display
    #     self.recTable.update(values=data)
