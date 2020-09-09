import tkinter as tk
import tkinter.messagebox as tkmb
from recipeCreator import *
import csv, json, yaml, sys, logging, re
import sqlite3 as sql
import requests as rq
from contextlib import suppress
from database import *
from tkinter import N,E,S,W
from apiCalls import *
from KitchenGUI.searchBar import searchBar
from KitchenGUI.table import table
from KitchenGUI.helpers import resizeSetup

global logger
logger = logging.getLogger('Debug Log')

class mainGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.rows = []
        self.master = master

        resizeSetup(self.master)
        resizeSetup(self, rows=3, cols=1)
        self.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        self.db = database(returnRecipe=False)
        self.table = self.recipeTable()
        self.rec = self.recView()
        self.bar = self.toolbar()
        self.state = "recView"

        self.bar.grid(row=0, column=0, sticky=N+E+W)

        self.table.grid(row=1, column=0, sticky=N+E+W)

        self.rec.grid(row=2, column=0, sticky=N+E+S+W)

    def recView(self, recipe=None):
        """This is the recipe view, is allows for creating new recipes and
        editing current recipes. If recipe is given, data fields will be filled
        recipe information"""
        # Content Frame
        content = tk.Frame(master=self)
        resizeSetup(content, rows=10, cols=2)

        # Simpler fields are repeated as Entries
        simpleFields = ('Title', 'Prep Time', 'Cook Time', 'Yield', 'Category', 'Rating', 'Source')
        for i, field in enumerate(simpleFields):
            tk.Label(master=content, text=field)\
              .grid(row=i, column=0, sticky=N+E+S+W)
            tk.Entry(master=content, width=60)\
              .grid(row=i, column=1, sticky=N+E+S+W)

        # Directions
        tk.Label(master=content, text='Directions')\
          .grid(row=6, column=0, columnspan=2, sticky=N+E+S+W)
        tk.Text(master=content, height=10, width=60)\
          .grid(row=7, column=0, columnspan=2, sticky=N+E+S+W)

        # Ingredients
        tk.Label(master=content, text='Ingredients')\
        .grid(row=8, column=0, columnspan=2, sticky=N+E+S+W)
        ing = tk.Frame(master=content)
        resizeSetup(ing, rows=1, cols=1)
        ing.grid(row=9, column=0, columnspan=2, sticky=N+E+S+W)
        # tk.Text(master=content, height=10, width=60).pack()
        ingGuts = self.ingFrame(master=ing)
        ingGuts.grid(row=0, column=0, sticky=N+E+S+W)
        # ing.pack()
        return content

    def toolbar(self):
        bar = tk.Frame(master=self)
        self.back = tk.Button(master=bar, text="BACK")
        self.quit = tk.Button(master=bar, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.tableView = tk.Button(master=bar, text="Table View")

        resizeSetup(bar, rows=1, cols=5)
        # self.tableView.pack()
        self.tableView.grid(row=0, column=1, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        # self.quit.pack(side="right")
        self.quit.grid(row=0, column=4, sticky=tk.N+tk.S+tk.E+tk.W)
        # self.back.pack(side='left')
        self.back.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        return bar

    def ingFrame(self, master, rowCount=3, colCount=3):
        """This is a helper function for recView, it creates the ingredient adder section"""

        # content frame
        holder = tk.Frame(master=master)
        resizeSetup(holder, rows=3, cols=1)

        # search area
        # search = tk.Frame(master=holder)
        search = searchBar(master=holder)

        search.grid(row=0, column=0, sticky=N+E+W)

        # option selector
        options = tk.Frame(master=holder)
        resizeSetup(options, rows=6, cols=colCount+2)
        options.grid(row=1, column=0, sticky=N+E+S+W)

        # Buttons (Right of option table)
        # Up/Down buttons to scroll through options
        up = tk.Button(master=options, text='UP')
        up.grid(row=1, column=colCount+1, sticky=N+E+S+W)
        down = tk.Button(master=options, text='DOWN')
        down.grid(row=2, column=colCount+1, sticky=N+E+S+W)

        # amount field
        amount = tk.Entry(master=options)
        amount.grid(row=4, column=colCount+1, sticky=N+E+S+W)

        # add button
        add = tk.Button(master=options, text='Add')
        add.grid(row=5, column=colCount+1, sticky=N+E+S+W)

        blanks = [['[BLANK]'] * colCount for i in range(rowCount)]
        self.optionsTable = table(master=options,
                             rows=rowCount,
                             cols=colCount,
                             data=blanks,
                             innerWidget=tk.Button)
        self.optionsTable.grid(row=0, column=0, rowspan=6, columnspan=colCount, sticky=N+E+S+W)
        search.addFunc(func=lambda query: mainGui.getIngResults(self.optionsTable, query))

        # current ingredients
        current = tk.Frame(master=holder)
        resizeSetup(current, rows=1, cols=1)
        current.grid(row=2, column=0, sticky=N+E+S+W)
        currentText = tk.Text(master=current, height=10, width=60)
        currentText.grid(row=0, column=0, sticky=N+E+S+W)

        return holder

    @staticmethod
    def getIngResults(table, query):
        logger.debug(f'table={table}, query={query}')
        api = apiCalls()
        response = api.apiSearchFood(query)
        options = response.json()['foods']
        upperLimit = len(options) - 1
        data = blanks = [['[BLANK]'] * table.cols for i in range(table.rows)]
        for i in range(table.rows):
            data[i][0] = options[i]["description"][:25]
            with suppress(KeyError):
                if options[i]['dataType'] == 'Branded':
                    data[i][1] = options[i]["brandOwner"][:25]
                    data[i][2] = options[i]["ingredients"][:43]
                else:
                    data[i][2] = options[i]["additionalDescriptions"][:43]

        table.updateTable(data)


    def recipeTable(self, rowCount=1, colCount=6):
        """This is the table view, it displays the database, and allows searching
        the database"""
        # Acquire data
        header = self.db.getColumns('recipes')[:colCount]
        data = self.db.recipes(first=0, count=rowCount)
        # Combine into one dataframe
        allData = [header, *data]

        # Content Window holds all the table elements
        tableFrame = tk.Frame(master=self)
        resizeSetup(tableFrame, rows=2, cols=1)

        search = searchBar(master=tableFrame)
        search.grid(row=0, column=0, sticky= N+E+S+W)

        tab = table(master=tableFrame,
                      rows=rowCount+1,
                      cols=colCount,
                      data=allData,
                      innerWidget=tk.Button,
                      header=True,
                      style='alternating')
        tab.grid(row=1, column=0, sticky=N+E+S+W)

        # # Table Headers
        # for col in range(colCount):
        #     # table.columnconfigure(col, weight=1, minsize=75)
        #     frame = tk.Frame(
        #         master=table,
        #         relief=tk.RAISED,
        #         borderwidth=0
        #     )
        #     resizeSetup(frame)
        #     frame.grid(row=1, column=col, sticky=N+E+S+W)
        #     label = tk.Label(
        #         master=frame,
        #         text=f"{header[col]}",
        #     )
        #     label.grid(row=0, column=0, sticky=N+E+S+W)
        # # Fill table with data
        # for row in range(1,rowCount+1):
        #     # determine row resizing
        #     # table.rowconfigure(row, weight=1, minsize=50)
        #
        #     # determine the row color, switches between white and grey
        #     color = 'white'
        #     if row % 2 == 0:
        #         color = 'grey'
        #     for col in range(colCount):
        #         # determine column resizing
        #         table.columnconfigure(col, weight=1, minsize=75)
        #         #build frame
        #         frame = tk.Frame(
        #             master=table,
        #             relief=tk.RAISED,
        #             borderwidth=0,
        #             bg=color
        #         )
        #         resizeSetup(frame)
        #
        #         # fill with button
        #         frame.grid(
        #             row=row+1,
        #             column=col,
        #             ipadx=0,
        #             ipady=0,
        #             sticky=N+E+S+W
        #         )
        #
        #         label = tk.Button(
        #             master=frame,
        #             text=f"{allData[row][col]}",
        #             borderwidth=0,
        #             bg=color)
        #         label.grid(row=0, column=0, sticky=N+E+S+W)
        return tableFrame

    def say_hi(self):
        print("hi there, everyone!")

def main():
    root = tk.Tk()
    app = mainGui(master=root)

    # app = tk.Frame(master=root)
    # app.pack()
    # searchBar(master=app, func=print).pack()
    root.mainloop()

if __name__ == '__main__':
    main()
