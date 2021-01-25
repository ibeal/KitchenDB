import tkinter as tk
import tkinter.messagebox as tkmb
import csv, json, yaml, sys, logging, re
import sqlite3 as sql
import requests as rq
from contextlib import suppress
from containers.recipe  import *
from DB.database import *
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

        self.db = database()
        self.recFields = {}
        self.recTableDim = (5,6)
        self.table = self.recipeTable()
        self.rec = self.recView()
        self.bar = self.toolbar()
        self.state = {"lastTableAction": "default"}
        
        self.selectedIng = None
        self.bar.grid(row=0, column=0, sticky=N+E+W)

        self.table.grid(row=1, column=0, sticky=N+E+W)

        self.rec.grid(row=2, column=0, sticky=N+E+S+W)

    def recView(self, recipe=None):
        """This is the recipe view, is allows for creating new recipes and
        editing current recipes. If recipe is given, data fields will be filled
        recipe information"""
        # Content Frame
        content = tk.Frame(master=self)
        resizeSetup(content, rows=11, cols=2)

        bar = tk.Frame(master=content)
        bar.grid(row=0, column=0, columnspan=2, sticky=N+E+S+W)
        resizeSetup(bar, rows=1, cols=3)
        clear = tk.Button(master=bar, text="Clear", command=self.clearFields)
        clear.grid(row=0, column=0, sticky=N+S+W+E)
        delete = tk.Button(master=bar, text="Delete Recipe", command=self.delete)
        delete.grid(row=0, column=1, sticky=N+E+S+W)
        save = tk.Button(master=bar, text="Save", command=self.saveFields)
        save.grid(row=0, column=2, sticky=N+S+E+W)

        # Simpler fields are repeated as Entries
        simpleFields = ('Title', 'Prep Time', 'Cook Time', 'Yield', 'Category', 'Rating', 'Source')
        for i, field in enumerate(simpleFields, 1):
            tk.Label(master=content, text=field)\
              .grid(row=i, column=0, sticky=N+E+S+W)
            entry = tk.Entry(master=content, width=60)
            entry.grid(row=i, column=1, sticky=N+E+S+W)
            self.recFields[field] = entry

        # Directions
        tk.Label(master=content, text='Directions')\
          .grid(row=7, column=0, columnspan=2, sticky=N+E+S+W)
        dirs = tk.Text(master=content, height=10, width=60)
        dirs.grid(row=8, column=0, columnspan=2, sticky=N+E+S+W)
        self.recFields['Directions'] = dirs

        # Ingredients
        tk.Label(master=content, text='Ingredients')\
        .grid(row=9, column=0, columnspan=2, sticky=N+E+S+W)
        ing = tk.Frame(master=content)
        resizeSetup(ing, rows=1, cols=1)
        ing.grid(row=10, column=0, columnspan=2, sticky=N+E+S+W)
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
        self.tableView = tk.Button(master=bar, text="Table View",
                                   command=self.refreshRecipeTable)

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
        up = tk.Button(master=options, text='More')
        up.grid(row=1, column=colCount+1, sticky=N+E+S+W)
        down = tk.Button(master=options, text='Back')
        down.grid(row=2, column=colCount+1, sticky=N+E+S+W)

        # amount field
        amount = tk.Entry(master=options)
        amount.grid(row=4, column=colCount+1, sticky=N+E+S+W)

        # add button
        add = tk.Button(master=options,
                        text='Add')
        add.grid(row=5, column=colCount+1, sticky=N+E+S+W)

        blanks = [['[BLANK]'] * colCount for i in range(rowCount)]
        self.optionsTable = table(master=options,
                             rows=rowCount,
                             cols=colCount,
                             data=blanks,
                             innerWidget=tk.Button,
                             buttonCallback=lambda row, col, **kw: self.activateRow(self.optionsTable, row, col))
        self.optionsTable.grid(row=0, column=0, rowspan=6, columnspan=colCount, sticky=N+E+S+W)
        search.addFunc(func=lambda query, **kw: self.getIngResults(self.optionsTable, query, **kw))
        up['command'] = lambda: search.search(newQuery=False, up=True)
        down['command'] = lambda: search.search(newQuery=False, up=False)
        # current ingredients
        current = tk.Frame(master=holder)
        resizeSetup(current, rows=1, cols=1)
        current.grid(row=2, column=0, sticky=N+E+S+W)
        currentText = tk.Text(master=current, height=10, width=60)
        currentText.grid(row=0, column=0, sticky=N+E+S+W)
        self.recFields['Ingredients'] = currentText

        add["command"] = lambda: self.addIng(amount, currentText)

        return holder

    def addIng(self, entry, dest):
        """Add ingredient to the ingredient text box
        Input:
        self.optionsTable: Table from which to pull the data
        entry: the entry box that contains the amount
        dest: the text box to put the aquired ingredient
        """
        logger.debug('Add Ingredient Button pressed')
        amount = entry.get()
        if len(amount) <= 0:
            tkmb.showinfo('Amount Missing', 'The amount box is empty.')
        else:
            choice = self.optionsTable.fullData[self.selectedIng]
            ing = f"('{database.db_clean(choice['description'])}', {choice['fdcId']}, '{amount}')"
            dest.insert(tk.END, ing)
            dest.insert(tk.END, '\n')


    def activateRow(self, table, row, col):
        """Simple function to select a row
        Input:
        self.selectedIng: updated the selectedIng with the row clicked
        table: updates bg of all tiles in table (This should be moved to table logic)
        row: row of button Clicked
        col: col of button clicked

        The bg updating logic should be moved to the table class, and here should
        just call table.activate(row#, row=True)
        """
        logger.debug(f"row activated at {row}")
        self.selectedIng = row
        for r in table.tiles:
            for tile in r:
                tile["bg"] = 'white'
        for tile in table.tiles[row]:
            tile['bg'] = 'grey'

    def getIngResults(self, table, query, newQuery=True, up=True):
        """Ingredient Search Bar callback.
        Input:
        self.minimumIngChoice: uses this number to remember state of options
        self.selectedIng: resets this to clear the activated option
        table: given table is filled with the query data
        newQuery: bool, original query passes true, more/less buttons pass false
        up: bool, whether more or less was pressed (ignored if newQuery is true)
        Range for options is determined using newQuery, self.minimumIngChoice,
        and table.rows. Then data is fetched from food.gov, and the table is updated
        with the response data matching the range generated.
        """

        self.selectedIng = None
        if newQuery:
            self.minimumIngChoice = 0
            logger.debug(f'ingredient table range is 0 to {table.rows}')
        else:
            if up:
                self.minimumIngChoice += table.rows
            elif self.minimumIngChoice > table.rows - 1:
                self.minimumIngChoice -= table.rows
            logger.debug(f'ingredient table range is {self.minimumIngChoice} to {table.rows + self.minimumIngChoice}')
        logger.debug(f'table={table}, query={query}')
        api = apiCalls()
        response = api.apiSearchFood(query)
        options = response.json()['foods'][self.minimumIngChoice:table.rows + table.rows + self.minimumIngChoice]
        upperLimit = len(options) - 1
        data = [['[BLANK]'] * table.cols for i in range(table.rows)]
        for i in range(table.rows):
            data[i][0] = options[i]["description"][:25]
            with suppress(KeyError):
                if options[i]['dataType'] == 'Branded':
                    data[i][1] = options[i]["brandOwner"][:25]
                    data[i][2] = options[i]["ingredients"][:43]
                else:
                    data[i][2] = options[i]["additionalDescriptions"][:43]

        table.updateTable(data, fullData=options)


    def recipeTable(self):
        """This is the table view, it displays the database, and allows searching
        the database"""
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
        allData = [header, *data]

        # print(data)
        # Combine into one dataframe
        # pad allData with blank rows if there's not enough data

        # Content Window holds all the table elements
        tableFrame = tk.Frame(master=self)
        resizeSetup(tableFrame, rows=2, cols=1)

        search = searchBar(master=tableFrame, func=lambda query: self.searchdb(query))
        search.grid(row=0, column=0, sticky= N+E+S+W)

        tableCallback = lambda fullData, **kwargs: self.fillFields(fullData)
        self.recTable = table(master=tableFrame,
                      rows=rowCount+1,
                      cols=colCount,
                      data=allData,
                      innerWidget=tk.Button,
                      header=True,
                      style='alternating',
                      buttonCallback=tableCallback,
                      fullData=[header, *recs])
        self.recTable.grid(row=1, column=0, sticky=N+E+S+W)
        return tableFrame

    def searchdb(self, query):
        row, col = self.recTableDim
        # get search results
        recs = self.db.search(query)
        data = []
        header = recipe.pretty_fields[:col]
        for rec in recs:
            recInfo = rec.guts()
            temp = []
            for col in header:
                temp.append(recInfo[col])
            data.append(temp)

        # preppend header list
        data = [header, *data]
        # pass all data to update table
        self.state["lastTableAction"] = "search"
        self.state["lastSearch"] = query
        self.recTable.updateTable(data, fullData=[header, *recs])

    def fillFields(self, rec):
        """Function that will fill the recipe fields with the recipe data.
        Input:
        rec: recipe object with information to fill fields with
        """
        logger.debug("fill fields callback with:")
        logger.debug(rec)
        # rec.gets returns a dictionary with all the information in it
        for field, value in rec.guts().items():
            # SPOT becomes the starting point for the insert
            # 0 for entry objects, and "0.0" for text objects
            SPOT = 0
            if field == "Directions":
                SPOT = "0.0"
                # data preprocessing, each direction should be seperated with a newline
                value = '\n'.join(value)
                value += '\n'
            elif field == "Ingredients":
                SPOT = "0.0"
                # data preprocessing, each direction is grouped in three and seperated
                # with newlines
                value = '\n'.join([f'{a,b,c}' for a,b,c in value])
                value += '\n'
            # clear the field
            self.recFields[field].delete(SPOT, tk.END)
            # fill the field
            self.recFields[field].insert(SPOT, value)

    def clearFields(self):
        """Simple function that clears all the fields in the recipe view"""
        for field in self.recFields:
            # SPOT becomes the starting point for the insert
            # 0 for entry objects, and "0.0" for text objects
            SPOT = "0.0" if field in ["Directions", "Ingredients"] else 0
            # clear the field
            self.recFields[field].delete(SPOT, tk.END)

    def saveFields(self):
        """Function that records all the information in the fields and returns
        a recipe object. The object is sent to the database
        Input:
        self.recFields: dictionary of all the recipe fields
        self.db: database to send the information
        """
        # result object, it is a temp holder for the information
        res = {}
        # iterate over recFields, field is string name of field being analyzed,
        # value is the actual text/entry itself
        for field, value in self.recFields.items():
            if field == "Directions":
                # get info
                text = value.get("0.0", tk.END)
                # data preprocessing, three things going on
                # text.split('\n') returns list of lines in textbox
                # list comprehension goes over the list and removes empty strings
                # then the list is stringed
                res[field] = str([val for val in text.split('\n') if len(val) > 0])
            elif field == "Ingredients":
                text = value.get("0.0", tk.END)
                # only the first two things happen here
                temp = [val for val in text.split('\n') if len(val) > 0]
                # Additionally, the tuples are interpreted here,
                # then the whole thing is stringified
                res[field] = str([recipe.interp(s) for s in temp])
            else:
                # else, it's an entry box
                res[field] = value.get()
        # create the recipe, the list comprehension is to put the dictionary in order
        rec = recipe([res[key] for key in recipe.pretty_fields])

        if self.db.exists(rec.name):
            if tkmb.askyesno("Overwrite?", "This recipe already exists, do you want to overwrite it?"):
                # save to db
                self.db.delete(rec)
                self.db.save(rec)
        else:
            self.db.save(rec)
        self.refreshRecipeTable()

    def refreshRecipeTable(self):
        logger.debug("Refreshing recipe table")
        row, col = self.recTableDim
        if self.state["lastTableAction"] == "default":
            logger.debug("last state was default")
            recs = self.db.recipes(count=row)
        elif self.state["lastTableAction"] == "search":
            logger.debug("last state was search")
            recs = self.db.search(self.state["lastSearch"])
        # create data matrix
        data = []
        header = recipe.pretty_fields[:col]
        for rec in recs:
            recInfo = rec.guts()
            temp = []
            for col in header:
                temp.append(recInfo[col])
            data.append(temp)

        # preppend header list
        data = [header, *data]
        # chop off ing and dirs for display
        self.recTable.updateTable(data, fullData=recs)

    def delete(self):
        if tkmb.askyesno("Delete?", "Are you sure you want to delete this recipe?"):
            self.db.delete(self.recFields['Title'].get())
            self.clearFields()
            self.refreshRecipeTable()


def main():
    root = tk.Tk()
    app = mainGui(master=root)

    # app = tk.Frame(master=root)
    # app.pack()
    # searchBar(master=app, func=print).pack()
    root.mainloop()

if __name__ == '__main__':
    main()
