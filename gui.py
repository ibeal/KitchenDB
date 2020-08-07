from config import *
from recipeCreator import *
from database import *
import tkinter as tk

class mainGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.db = database()
        self.recipeRow()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def recipeRow(self):
        self.row = tk.Frame(self)
        rec = self.db.recipes(first=0, count=1)[0]
        for part in rec:
            tk.Label(master=self.row, text=str(part)).pack(side=tk.LEFT)
        self.row.pack()


    def say_hi(self):
        print("hi there, everyone!")

if __name__ == '__main__':
    root = tk.Tk()
    app = mainGui(master=root)
    app.mainloop()
