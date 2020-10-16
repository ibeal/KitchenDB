import logging
# import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
import PySimpleGUIQt as sg
import KitchenGUI.searchBar as search
from database import *
from recipeCreator import *
from apiCalls import *

class recipeTable(sg.Column):
    def __init__(self, master, *args, tableKey='-RECIPE-TABLE-', **kwargs):
        self.master = master
        self.db = self.master.db
        self.recTableDim = self.master.recTableDim
        self.tableKey = tableKey
        super().__init__(layout=self.createRecipeTable(), *args, **kwargs)

    def createRecipeTable(self):
        rowCount, colCount = self.recTableDim
        # Acquire data
        # note, the ingredients and directions are left off due to the number of columns
        header = recipe.pretty_fields[:colCount]
        recs = self.db.recipes(first=0, count=rowCount)
        data = []
        for rec in recs:
            recInfo = rec.guts()
            temp = []
            for col in header:
                temp.append(recInfo[col])
            data.append(temp)
        # allData = [header, *data]
        self.tableData = recs
        self.master.tableData = recs
        self.recTable = sg.Table(data,
                                headings=header,
                                num_rows=rowCount,
                                enable_events=True,
                                col_widths=[24, 9, 9, 20, 9, 6],
                                auto_size_columns=False,
                                key=self.tableKey)
        # col = sg.Column(layout = tab, scrollable=True)
        self.master.expands['xy'].append(self.recTable)
        layout = [search.searchBar(self.master,key='RECIPE'),
                  [self.recTable]]
        # return sg.Column(layout=layout,expand_x=True,expand_y=True,justification='center')
        return layout
