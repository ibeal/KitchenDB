
from KitchenGUI.helpers import resizeSetup
import tkinter as tk
from tkinter import N,E,S,W
from copy import deepcopy,copy

class table(tk.Frame):
    def __init__(self,
                master=None,
                rows=1,
                cols=1,
                data=[['Default Data']],
                innerWidget=tk.Label,
                buttonCallback=None,
                header=False,
                style='default',
                fullData=None):
        """
        parameters:
        master: the master frame for the table
        rows: number of rows
        cols: number of columns
        data: list of lists (matrix) containing data to display
        innerWidget: the type of the individual elements of the table
        buttonCallback: The function that is called when the button is clicked
        header: bool, whether or not the first row is a header row
        style: string, right now just accepts alternating, meaning that the color alternates
        """
        super().__init__(master)
        resizeSetup(self)
        self.master = master
        self.rows=rows
        self.cols=cols
        self.data=data
        if not fullData:
            self.fullData = data
        else:
            self.fullData = fullData
        self.innerWidget=innerWidget
        self.callback=buttonCallback
        self.header=header
        self.style=style
        self.content = tk.Frame(master=self)
        resizeSetup(self.content, rows=self.rows, cols=self.cols)
        self.content.grid(row=0, column=0, sticky=N+E+S+W)
        self.tiles = [['[BLANK]'] * self.cols for i in range(self.rows)]
        self.fillTable()


    def fillTable(self):
        """generates the content table"""
        # number of rows
        rows = range(self.rows)

        # header loop
        if self.header:
            # Table Headers
            for col in range(self.cols):
                self.tiles[0][col] = tk.Frame(
                    master=self.content,
                    relief=tk.RAISED,
                    borderwidth=0
                )
                resizeSetup(self.tiles[0][col])
                self.tiles[0][col].grid(row=0, column=col, sticky=N+E+S+W)
                label = tk.Label(
                    master=self.tiles[0][col],
                    text=f"{self.data[0][col]}",
                )
                label.grid(row=0, column=0, sticky=N+E+S+W)
            # modify the rows to skip the first row (header row)
            rows = range(1, self.rows)

        # create each row
        for row in rows:
            # background color
            color = 'white'

            # if using alternating, alternate colors each row
            if self.style == 'alternating' and row % 2 == 0:
                color = 'grey'

            for col in range(self.cols):
                self.tiles[row][col] = self.innerWidget(
                    master=self.content,
                    text=self.data[row][col],
                    bd=0,
                    bg=color)
                # if using button, a callback can be supplied
                if self.innerWidget == tk.Button:
                    self.tiles[row][col]['command'] = lambda row=row, col=col: self.callback(row=row, col=col)
                self.tiles[row][col].grid(row=row, column=col, sticky=N+E+S+W)

    def updateTable(self, data, fullData=None):
        """updates the table with new data"""
        # updates the data property
        self.data = data
        if not fullData:
            self.fullData = data
        else:
            self.fullData = fullData
        self.content.destroy()
        self.tiles = [['[BLANK]'] * self.cols for i in range(self.rows)]
        self.content = tk.Frame(master=self)
        resizeSetup(self.content, rows=self.rows, cols=self.cols)
        self.content.grid(row=0, column=0, sticky=N+E+S+W)
        self.fillTable()

    @staticmethod
    def main():
        """main driver for table, will eventually become a unit test"""
        root = tk.Tk()
        resizeSetup(root)
        # app = mainGui(master=root)
        stuff = [["another", 'word'], ['2 words', 'words']]
        app = tk.Frame(master=root)
        resizeSetup(app)
        app.grid(row=0, column=0, sticky=N+E+S+W)
        table(master=app, rows=2, cols=2, data=stuff)\
        .grid(row=0, column=0, sticky=N+E+S+W)
        root.mainloop()

if __name__ == "__main__":
    table.main()
