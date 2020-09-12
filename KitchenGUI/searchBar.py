import tkinter as tk
import tkinter.messagebox as tkmb
from KitchenGUI.helpers import resizeSetup
from tkinter import N,E,S,W

class searchBar(tk.Frame):
    def __init__(self, master=None, func=None):
        super().__init__(master)
        self.master = master
        self.func = func

        resizeSetup(self, rows=1, cols=5)

        self.searchEntry = tk.Entry(master=self)
        self.searchEntry.grid(row=0, column=0, columnspan=4, sticky=N+E+S+W)

        self.searchButton = tk.Button(master=self,
                                      text='Search',
                                      command=self.search)
        self.searchButton.grid(row=0, column=4, sticky=N+E+S+W)
        # print('finished')
        # self.func('finished')

    def addFunc(self, func):
        self.func = func

    def search(self, **kw):
        # logger.debug('Search Button Clicked, callback function called')
        # print('callback called')
        if self.func:
            self.func(self.searchEntry.get(), **kw)

    @staticmethod
    def main():
        root = tk.Tk()

        app = tk.Frame(master=root)
        app.pack()
        searchBar(master=app, func=print).pack()
        root.mainloop()
