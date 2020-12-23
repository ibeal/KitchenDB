import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
import KitchenGUI.searchBar as searchBar
from DB.database import *
from recipeCreator import *
from apiCalls import *
from KitchenModel import *
from views.view import view
from controllers.recipeTableController import *
logger = logging.getLogger('Debug Log')

class recipeTable(sg.Tab, view):
    def __init__(self, title, master, *args, tableKey='-RECIPE-TABLE-', **kwargs):
        self.model = KitchenModel.getInstance()
        self.master = master
        self.recTableDim = self.master.recTableDim
        self.tableKey = tableKey
        self.features = ['Title', 'Prep Time', 'Cook Time', 'Yield', 'Category', 'Rating']
        self.header = ['Title', 'Prep', 'Cook', 'Yield', 'Category', 'Rating']
        super().__init__(title, layout=self.createRecipeTable(), *args, **kwargs)
        self.model.addTab("-TABLE-", self, recipeTableController(),
            {"tableKey":self.tableKey,
             "features":self.features,
             "recTable":self.recTable,
             "tableData":self.tableData,
             "recTableDim":self.recTableDim})
        # self.controller = recipeTableController(self.tableKey, self.features, self.recTable, self.tableData, self.recTableDim)

    def refreshView(self, model, key):
        if key == "active_view":
            if self.model.get("active_view") == "-TABLE-":
                self.Select()
        else:
            self.refreshRecipeTable()
            self.model.set("tabData", "-TABLE-", "tableData", value=self.tableData, notify=False)

    def createRecipeTable(self):
        rowCount, colCount = self.recTableDim
        # Acquire data
        # note, the ingredients and directions are left off due to the number of columns
        # header = recipe.pretty_fields[:colCount]
        recs = self.model.get('RecipeAPI').recipes(first=0, count=rowCount)
        data = []
        for rec in recs:
            recInfo = rec.guts()
            temp = []
            for col in self.features:
                temp.append(recInfo[col])
            data.append(temp)
        # allData = [self.header, *data]
        self.tableData = recs
        # self.master.tableData = recs
        self.recTable = sg.Table(data,
                                headings=self.header,
                                num_rows=rowCount,
                                enable_events=True,
                                col_widths=[24, 4, 4, 20, 9, 6],
                                auto_size_columns=False,
                                key=self.tableKey,
                                tooltip="This is a table of your recipes, search options are above, and clicking on a recipe will open it in the editor")
        # col = sg.Column(layout = tab, scrollable=True)
        # self.master.expands['xy'].append(self.recTable)
        layout = [
            [
              sg.T('Sort By'),
              sg.Combo(default_value='None', values=['None', 'Title', 'Category', 'Rating'], key='-TABLE-SORT-',
                    tooltip="Choose which field to sort the next search by",
                    disabled=True)
            ],
            [
              *searchBar.searchBar(self.master,key='RECIPE',
                    tooltip="Enter the recipe title you are looking for"),
              sg.Button('Add New Recipe', key='-ADDNEW-',
                    tooltip="Click here for a blank new recipe")],
            [self.recTable]
        ]
        # return sg.Column(layout=layout,expand_x=True,expand_y=True,justification='center')
        return layout

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

        # pass all data to update table

        # can't notify after first set, because data isn't complete
        self.model.set("state", "lastTableAction", value="search", notify=False)
        # I could notify after the second one, but for now it's not needed
        self.model.set("state", "lastSearch", value=query, notify=False)
        self.tableData = recs
        self.recTable.update(values = data)

    def refreshRecipeTable(self):
        logger.debug("Refreshing recipe table")
        row, col = self.recTableDim
        if self.model.get("state", "lastTableAction") == "default":
            logger.debug("last state was default")
            recs = self.model.get('RecipeAPI').recipes(count=row)
        elif self.model.get("state", "lastTableAction") == "search":
            logger.debug("last state was search")
            recs = self.model.get('RecipeAPI').search(self.model.get("state", "lastSearch"))
        else:
            raise Exception("Unknown last state!")
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
