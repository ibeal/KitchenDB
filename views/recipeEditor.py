import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
import KitchenGUI.searchBar as searchBar
from DB.database import *
from recipeCreator import *
from apiCalls import *
from KitchenModel import *
from views.view import view
from controllers.recipeEditorController import *
logger = logging.getLogger('Debug Log')

class recipeEditor(sg.Tab, view):

    def __init__(self, title, master, *args, ingTableKey = '-OPTION-TABLE-', **kwargs):
        self.model = KitchenModel.getInstance()
        self.master = master
        self.ingTableKey = ingTableKey
        self.recFields = {field: f'-{field}-BOX-' for field in recipe.pretty_fields}
        super().__init__(title, layout=self.recipeEditor(), *args, **kwargs)

        self.model.addTab("-EDITOR-", self, recipeEditorController(), {"recFields":self.recFields, "ingTableKey":self.ingTableKey})
        # self.model.seta("tabData", "-EDITOR-", value={"recFields":self.recFields, "ingTableKey":self.ingTableKey})
        # self.controller = recipeEditorController(self.recFields, self.ingTableKey)

    def labeledEntry(self,label,key=None,**kwargs):
        box = sg.In(key=f'-{key if key else label}-BOX-',**kwargs)
        return [sg.T(label),box]

    def update(self, data):
        self.table = data
        self.ingTable.update(data)

    def refreshView(self, model, key):
        if key == "activeRecipe":
            self.fillFields(self.model.get('activeRecipe'))
        elif key == "active_view":
            if self.model.get("active_view") == "-EDITOR-":
                self.Select()

    def recipeEditor(self):
        simpleFields = [field for field in recipe.pretty_fields]
        simpleFields.remove('Ingredients')
        simpleFields.remove('Directions')
        simpleInputs = [
            self.labeledEntry('Title'),
            [
                *self.labeledEntry('Prep Time',size=(10,1)),
                *self.labeledEntry('Cook Time',size=(10,1)),
                *self.labeledEntry('Total Time',size=(5,1))
            ],
            [
                *self.labeledEntry('Yield',size=(10,1)),
                *self.labeledEntry('Category',size=(10,1)),
                *self.labeledEntry('Rating',size=(5,1))
            ],
            [*self.labeledEntry('Source'), sg.Button('AutoFill', key="-AUTOFILL-", disabled=True)]
        ]
        # self.master.recFields = {field: simpleInputs[field][1] for field in simpleFields}


        # data = [['BLANK']*3 for i in range(3)]
        data = []

        self.ingTable = sg.Table(data,
                                num_rows=5,
                                headings=['Food', 'Company', 'Ingredients'],
                                col_widths=[8, 20, 40],
                                auto_size_columns=False,
                                key=self.ingTableKey)
        self.master.expands['x'].append(self.ingTable)

        dir = sg.Multiline(key='-Directions-BOX-',size=(50,10))
        self.master.expands['xy'].append(dir)
        # self.master.recFields['Directions'] = dir

        ing = sg.Multiline(key='-Ingredients-BOX-',size=(50,10))
        self.master.expands['xy'].append(ing)
        # self.master.recFields['Ingredients'] = ing

        addbox = [sg.T('Amount'), sg.In(key='-AMOUNT-')]
        self.master.expands['x'].append(addbox)
        layout = [
                [sg.Button('Clear',key='-CLEAR-RECIPE-'),
                 sg.Button('Delete Recipe',key='-DELETE-RECIPE-'),
                 sg.Button('View Recipe', key='-VIEW-RECIPE-'),
                 sg.Button('Save',key='-SAVE-RECIPE-')],
                *simpleInputs,
                [sg.T('Directions')],
                [dir],
                [sg.T('Ingredients')],
                searchBar.searchBar(self.master, key='INGREDIENT'),
                [self.ingTable],
                [*addbox, sg.Button('Add',key='-ADD-INGREDIENT-')],
                [ing]
        ]

        # col = sg.Column(layout=layout,expand_x=True,expand_y=True,justification='center')
        # self.master.expands['xy'].append(col)
        return layout

    def fillFields(self, rec):
        """Function that will fill the recipe fields with the recipe data.
        Input:
        rec: recipe object with information to fill fields with
        """
        logger.debug("fill fields callback with:")
        logger.debug(rec)
        # self.model.set('activeRecipe', rec)
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
            self.master.window[self.recFields[field]].update(value=value)
            # self.master.window.fill({self.recFields[field]: value})

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
            self.master.window[self.recFields['Ingredients']].update(value=ing, append=True)

    def clearFields(self):
        """Simple function that clears all the fields in the recipe view"""
        for field in self.recFields:
            # clear the field
            self.master.window[self.recFields[field]].update(value='')

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
            value = self.master.window[self.recFields[field]]
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
        return recipe(res) if len(res['Title']) > 0 else None

    def saveFields(self):
        """Function that records all the information in the fields and returns
        a recipe object. The object is sent to the database
        Input:
        self.recFields: dictionary of all the recipe fields
        self.model.db: database to send the information
        """

        # result object, it is a temp holder for the information
        res = {}
        # iterate over recFields, field is string name of field being analyzed,
        # value is the actual text/entry itself
        for field in recipe.pretty_fields:
            value = self.master.window[self.recFields[field]]
            if not field in ['Source']:
                if len(value.get()) <= 0:
                    sg.PopupError(f"Missing the {field} field!")
                    return
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
        rec = recipe(res)
        if self.model.get('db').recipeExists(rec.title, rec.source):
            if sg.popup_yes_no("This recipe already exists, do you want to overwrite it?", title="Overwrite?"):
                # save to db
                self.model.get('db').deleteRecipe(rec)
                self.model.get('db').saveRecipe(rec)
        else:
            self.model.get('db').saveRecipe(rec)

    def deleteRecipe(self):
        if sg.popup_yes_no("Are you sure you want to delete this recipe?", title="Delete?"):
            self.model.get('db').deleteRecipe(self.master.window[self.recFields['Title']].get())
            self.clearFields()

    # def searchdb(self, query):
    #     row, col = self.recTableDim
    #     # get search results
    #     recs = self.model.get('db').search(query)
    #     data = []
    #     header = recipe.pretty_fields[:col]
    #     for rec in recs:
    #         recInfo = rec.guts()
    #         temp = []
    #         for col in header:
    #             temp.append(recInfo[col])
    #         data.append(temp)
    #
    #     # preppend header list
    #     # data = [header, *data]
    #     # pass all data to update table
    #     self.model.seta("state", "lastTableAction", value="search", notify=False)
    #     self.model.seta("state", "lastSearch", value=query, notify=False)
    #     self.tableData = recs
    #     self.recTable.update(values = data)

    def recipe_modal(self, rec):
        sg.popup(rec.__str__());

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
        response = self.model.get('api').apiSearchFood(query)
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
