from recipeCreator import *
from database import *

from recView import *
from table import *
from tableView import *
from mainGui import *

if __name__ == '__main__':
    root = tk.Tk()
    app = mainGui(master=root)
    app.mainloop()
