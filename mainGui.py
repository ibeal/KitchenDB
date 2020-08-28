import tkinter as tk
from recipeCreator import *
from libs import *
from config import *
from database import *
from tkinter import N,E,S,W

def resizeSetup(target, rows=1, cols=1):
    for row in range(rows):
        tk.Grid.rowconfigure(target, row, weight=1)
    for col in range(cols):
        tk.Grid.columnconfigure(target, col, weight=1)

class mainGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.rows = []
        self.master = master

        resizeSetup(self.master)
        resizeSetup(self, rows=3, cols=1)
        self.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        # self.pack()
        # self.create_widgets()
        self.db = database()
        self.table = self.recipeTable()
        self.rec = self.recView()
        self.bar = self.toolbar()
        self.state = "recView"
        # self.bar.pack(side=tk.TOP, fill=tk.BOTH)
        self.bar.grid(row=0, column=0, sticky=N+E+W)
        # self.table.pack(fill=tk.BOTH)
        self.table.grid(row=1, column=0, sticky=N+E+W)
        # self.rec.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.rec.grid(row=2, column=0, sticky=N+E+S+W)

    def create_widgets(self):
        self.hi_there = tk.Button(master=self)
        # self.hi_there["text"] = "Hello World\n(click me)"
        # self.hi_there["command"] = self.say_hi
        # self.hi_there.pack(side="top")

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

    def ingFrame(self, master, rowCount=3, colCount=5):
        """This is a helper function for recView, it creates the ingredient adder section"""

        # content frame
        holder = tk.Frame(master=master)
        resizeSetup(holder, rows=3, cols=1)

        # search area
        searchBar = tk.Frame(master=holder)
        resizeSetup(searchBar, rows=1, cols=5)
        searchBar.grid(row=0, column=0, sticky=N+E+W)

        # search bar and button
        searchEntry = tk.Entry(master=searchBar)
        searchEntry.grid(row=0, column=0, columnspan=4, sticky=N+E+S+W)
        search = tk.Button(master=searchBar, text='Search')
        search.grid(row=0, column=4, sticky=N+E+S+W)

        # option selector
        options = tk.Frame(master=holder)
        resizeSetup(options, rows=6, cols=colCount+1)
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

        # table containing ingredient options
        optionsTable = tk.Frame(master=options)
        resizeSetup(optionsTable, rows=rowCount, cols=colCount)
        optionsTable.grid(row=0, column=0, rowspan=6, columnspan=5, sticky=N+E+S+W)

        # fill with data
        for row in range(rowCount):
            for col in range(colCount):
                label = tk.Button(master=optionsTable, text='[Blank]')
                label.grid(row=row, column=col, sticky=N+E+S+W)
                # label
                # optionsTable


        # current ingredients
        current = tk.Frame(master=holder)
        resizeSetup(current, rows=1, cols=1)
        current.grid(row=2, column=0, sticky=N+E+S+W)
        currentText = tk.Text(master=current, height=10, width=60)
        currentText.grid(row=0, column=0, sticky=N+E+S+W)

        return holder

    def recipeTable2(self, rowCount=1, colCount=6):
        """This is the table view, it displays the database, and allows searching
        the database"""
        # Acquire data
        header = self.db.getColumns('recipes')[:colCount]
        data = self.db.recipes(first=0, count=rowCount)
        # Combine into one dataframe
        allData = [header, *data]
        # Content Window holds all the table elements
        table = Table(master=self.master, rows=rowCount, cols=colCount,
                        innerWidget=tk.Button, data=allData)

        return table

    def recipeTable(self, rowCount=1, colCount=6):
        """This is the table view, it displays the database, and allows searching
        the database"""
        # Acquire data
        header = self.db.getColumns('recipes')[:colCount]
        data = self.db.recipes(first=0, count=rowCount)
        # Combine into one dataframe
        allData = [header, *data]
        # Content Window holds all the table elements
        table = tk.Frame(master=self)
        resizeSetup(table, rows=rowCount+1, cols=colCount)

        # Table Headers
        for col in range(colCount):
            table.columnconfigure(col, weight=1, minsize=75)
            frame = tk.Frame(
                master=table,
                relief=tk.RAISED,
                borderwidth=0
            )
            resizeSetup(frame)
            frame.grid(row=0, column=col, sticky=N+E+S+W)
            label = tk.Label(
                master=frame,
                text=f"{header[col]}",
            )
            label.grid(row=0, column=0, sticky=N+E+S+W)
        # Fill table with data
        for row in range(1,rowCount+1):
            # determine row resizing
            table.rowconfigure(row, weight=1, minsize=50)

            # determine the row color, switches between white and grey
            color = 'white'
            if row % 2 == 1:
                color = 'grey'
            for col in range(colCount):
                # determine column resizing
                table.columnconfigure(col, weight=1, minsize=75)
                #build frame
                frame = tk.Frame(
                    master=table,
                    relief=tk.RAISED,
                    borderwidth=0,
                    bg=color
                )
                resizeSetup(frame)
                
                # fill with button
                frame.grid(
                    row=row,
                    column=col,
                    ipadx=0,
                    ipady=0,
                    sticky=N+E+S+W
                )

                label = tk.Button(
                    master=frame,
                    text=f"{allData[row][col]}",
                    borderwidth=0,
                    bg=color)
                label.grid(row=0, column=0, sticky=N+E+S+W)
        return table

    def say_hi(self):
        print("hi there, everyone!")

if __name__ == '__main__':
    root = tk.Tk()
    app = mainGui(master=root)
    app.mainloop()
