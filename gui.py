from config import *
from recipeCreator import *
from database import *
import tkinter as tk

class mainGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.rows = []
        self.master = master
        self.pack()
        self.create_widgets()
        self.db = database()
        self.table = self.recipeTable()
        # self.recView()

    def create_widgets(self):
        self.hi_there = tk.Button(master=self.master)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(master=self.master, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def recView(self):
        """This is the recipe view, is allows for creating new recipes and
        editing current recipes"""
        # Content Frame
        content = tk.Frame(master=self.master)
        # Simpler fields are repeated as Entries
        simpleFields = ('Title', 'Prep Time', 'Cook Time', 'Yield', 'Category', 'Rating', 'Source')
        for field in simpleFields:
            tk.Label(master=content, text=field).pack()
            tk.Entry(master=content).pack()
        # Ingredients
        tk.Label(master=content, text='Ingredients').pack()
        tk.Text(master=content).pack()
        # Directions
        tk.Label(master=content, text='Directions').pack()
        tk.Text(master=content).pack()
        # pack then return
        content.pack(side=tk.TOP, fill=tk.BOTH)
        return content

    def recipeTable(self, rowCount=1, colCount=6):
        """This is the table view, it displays the database, and allows searching
        the database"""
        # Acquire data
        header = self.db.getColumns('recipes')[:colCount]
        data = self.db.recipes(first=0, count=rowCount)
        # Combine into one dataframe
        allData = [header, *data]
        # Content Window holds all the table elements
        table = tk.Frame(master=self.master)
        table.pack(side=tk.TOP, fill=tk.BOTH)

        # Table Headers
        for col in range(colCount):
            table.columnconfigure(col, weight=1, minsize=75)
            frame = tk.Frame(
                master=table,
                relief=tk.RAISED,
                borderwidth=0
            )
            frame.grid(row=0, column=col)
            label = tk.Label(
                master=frame,
                text=f"{header[col]}",
            )
            label.pack()
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
                # fill with button
                frame.grid(
                    row=row,
                    column=col,
                    ipadx=0,
                    ipady=0
                )
                label = tk.Button(
                    master=frame,
                    text=f"{allData[row][col]}",
                    borderwidth=0,
                    bg=color)
                label.pack()
        return table

    def say_hi(self):
        print("hi there, everyone!")

if __name__ == '__main__':
    root = tk.Tk()
    app = mainGui(master=root)
    app.mainloop()
