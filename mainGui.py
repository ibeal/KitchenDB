import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from database import *
from recipeCreator import recipe
from apiCalls import *
from KitchenGUI import recipeEditor as editor
from KitchenGUI import recipeTable as tableTab

class gui:

    def __init__(self):
        self.db = database()
        self.api = apiCalls()

        self.recFields = {field: f'-{field}-BOX-' for field in recipe.pretty_fields}
        self.recTableDim = (20,6)
        self.tableData = None

        self.expands = {'x':[], 'y':[], 'xy':[]}
        self.menu_def = [['&File', ['&Open', '&Save', '---', 'Properties', 'E&xit'  ]],
        ['&Edit', ['Paste', ['Special', 'Normal',], 'Undo'],],
        ['&Help', '&About...'],]
        self.state = {"lastTableAction": "default"}

        # self.layout = [
        #     [sg.Menu(self.menu_def)],
        #     [self.recipeTable()],
        #     [editor.recipeEditor(self,expand_x=True,expand_y=True,justification='center')]
        # ]
        # self.tableDisplay = sg.Tab('Recipe Table', [[self.recipeTable()]])
        self.recTable = '-RECIPE-TABLE-'
        self.tableDisplay = sg.Tab('Recipe Table',
            [[tableTab.recipeTable(self,tableKey=self.recTable, expand_x=True,
            expand_y=True,justification='center')]])
        self.editorDisplay = sg.Tab('Recipe Editor',
                                [[editor.recipeEditor(self,expand_x=True,
                                expand_y=True,justification='center')]])

        self.tabHolder = sg.TabGroup([
            [self.tableDisplay],
            [self.editorDisplay]
        ])
        self.expands['xy'].append(self.tabHolder)

        # Tabbed Layout
        self.layout = [
            [sg.Menu(self.menu_def)],
            [self.tabHolder]
        ]

        self.window = sg.Window('Window Title',
                                self.layout,
                                finalize=True,
                                resizable=True)

        for item in self.expands['x']:
            item.expand(expand_x=True)
        for item in self.expands['y']:
            item.expand(expand_y=True)
        for item in self.expands['xy']:
            item.expand(expand_x=True,expand_y=True)

    def mainLoop(self):
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            elif event == '-RECIPE-TABLE-':
                self.editorDisplay.Select()
                self.fillFields(self.tableData[values['-RECIPE-TABLE-'][0]])
            elif event =='-PRINT-RECIPE-':
                self.recipe_modal(self.getFields())
            elif event == '-SAVE-RECIPE-':
                self.saveFields()
            elif event == '-DELETE-RECIPE-':
                self.deleteRecipe()
                self.tableDisplay.Select()
            elif event == '-CLEAR-RECIPE-':
                self.clearFields()
            elif event == '-RECIPE-SBUTTON-':
                self.searchdb(values['-RECIPE-SBOX-'])
            elif event == '-INGREDIENT-SBUTTON-':
                self.getIngResults(values['-INGREDIENT-SBOX-'])
            elif event == '-ADD-INGREDIENT-':
                self.addIng(values['-OPTION-TABLE-'][0], values['-AMOUNT-'])

        self.window.close()

    def fillFields(self, rec):
        """Function that will fill the recipe fields with the recipe data.
        Input:
        rec: recipe object with information to fill fields with
        """
        logger.debug("fill fields callback with:")
        logger.debug(rec)

        # rec.gets returns a dictionary with all the information in it
        for field, value in rec.guts().items():
            if field == "Directions":
                # data preprocessing, each direction should be seperated with a newline
                value = '\n'.join(value)
                value += '\n'
            elif field == "Ingredients":
                # data preprocessing, each direction is grouped in three and seperated
                # with newlines
                value = '\n'.join([f'{a,b,c}' for a,b,c in value])
                value += '\n'
            # clear the field
            # self.recFields[field].delete(SPOT, tk.END)
            # fill the field
            self.window[self.recFields[field]].update(value=value)
            # self.window.fill({self.recFields[field]: value})

    def addIng(self, choice, entry):
        """Add ingredient to the ingredient text box
        Input:
        self.optionsTable: Table from which to pull the data
        entry: the entry box that contains the amount
        dest: the text box to put the aquired ingredient
        """
        logger.debug('Add Ingredient Button pressed')
        amount = entry
        if len(amount) <= 0:
            sg.popup('The amount box is empty.',title='Amount Missing')
        else:
            choice = self.ingTableData[choice]
            ing = f"('{database.aposFilter(choice['description'])}', {choice['fdcId']}, '{amount}')\n"
            self.recFields['Ingredients'].update(value=ing, append=True)

    def getIngResults(self, query, limit=25):
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

        logger.debug(f'Searching for ingredients. query={query}')
        response = self.api.apiSearchFood(query)
        options = response.json()['foods'][:limit]
        # data = [['[BLANK]'] * table.cols for i in range(table.rows)]
        data = []
        for i in range(len(options)):
            data.append([])
            data[i].append(options[i]["description"][:25])
            with suppress(KeyError):
                if options[i]['dataType'] == 'Branded':
                    data[i].append(options[i]["brandOwner"][:25])
                    data[i].append(options[i]["ingredients"][:43])
                else:
                    data[i].append(options[i]["additionalDescriptions"][:43])
        self.ingTableData = options
        self.ingTable.update(values=data)

    def clearFields(self):
        """Simple function that clears all the fields in the recipe view"""
        for field in self.recFields:
            # clear the field
            self.window[self.recFields[field]].update(value='')

    def getFields(self):
        """Function that records all the information in the fields and returns
        a recipe object.
        Input:
        self.recFields: dictionary of all the recipe fields
        Output:
        recipe: recipe created from all the fields
        """
        # result object, it is a temp holder for the information
        res = {}
        # iterate over recFields, field is string name of field being analyzed,
        # value is the actual text/entry itself
        for field in recipe.pretty_fields:
            value = self.window[self.recFields[field]]
            if field == "Directions":
                # get info
                text = value.get()
                # data preprocessing, three things going on
                # text.split('\n') returns list of lines in textbox
                # list comprehension goes over the list and removes empty strings
                # then the list is stringed
                res[field] = str([val for val in text.split('\n') if len(val) > 0])
            elif field == "Ingredients":
                text = value.get()
                # only the first two things happen here
                temp = [val for val in text.split('\n') if len(val) > 0]
                # Additionally, the tuples are interpreted here,
                # then the whole thing is stringified
                res[field] = str([recipe.interp(s) for s in temp])
            else:
                # else, it's an entry box
                res[field] = value.get()
        # create the recipe, the list comprehension is to put the dictionary in order

        # return recipe([res[key] for key in recipe.pretty_fields])
        return recipe(res)

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
        for field in recipe.pretty_fields:
            print(field)
            value = self.window[self.recFields[field]]
            if field == "Directions":
                # get info
                text = value.get()
                # data preprocessing, three things going on
                # text.split('\n') returns list of lines in textbox
                # list comprehension goes over the list and removes empty strings
                # then the list is stringed
                res[field] = str([val for val in text.split('\n') if len(val) > 0])
            elif field == "Ingredients":
                text = value.get()
                # only the first two things happen here
                temp = [val for val in text.split('\n') if len(val) > 0]
                # Additionally, the tuples are interpreted here,
                # then the whole thing is stringified
                res[field] = str([recipe.interp(s) for s in temp])
            else:
                # else, it's an entry box
                res[field] = value.get()
        # create the recipe, the list comprehension is to put the dictionary in order
        # rec = recipe([res[key] for key in recipe.pretty_fields])
        print(res)
        rec = recipe(res)

        if self.db.recipeExists(rec.name):
            if sg.popup_yes_no("This recipe already exists, do you want to overwrite it?", title="Overwrite?"):
                # save to db
                self.db.deleteRecipe(rec)
                self.db.saveRecipe(rec)
        else:
            self.db.saveRecipe(rec)
        self.refreshRecipeTable()

    def deleteRecipe(self):
        if sg.popup_yes_no("Are you sure you want to delete this recipe?", title="Delete?"):
            self.db.deleteRecipe(self.window[self.recFields['Title']].get())
            self.clearFields()
            self.refreshRecipeTable()

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
        # data = [header, *data]
        # pass all data to update table
        self.state["lastTableAction"] = "search"
        self.state["lastSearch"] = query
        self.tableData = recs
        self.recTable.update(values = data)

    def recipe_modal(self, rec):
        sg.popup(rec.__str__());

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
        # data = [header, *data]
        self.tableData = recs
        # chop off ing and dirs for display
        self.window[self.recTable].update(values=data)


def main():
    g = gui()
    g.mainLoop()

if __name__ == '__main__':
    main()
