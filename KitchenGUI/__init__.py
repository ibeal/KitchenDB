from recipeCreator import *
from database import *

from KitchenGUI.recView import *
from KitchenGUI.table import *
from KitchenGUI.tableView import *
from mainGui import *

def main():
    root = tk.Tk()
    app = mainGui(master=root)
    app.mainloop()
