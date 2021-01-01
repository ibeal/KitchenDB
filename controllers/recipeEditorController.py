import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
import KitchenGUI.searchBar as search
from DB.database import *
from containers.recipe import *
from apiCalls import *
from KitchenModel import *
from controllers.controller import controller
logger = logging.getLogger('recipeEditorController Log')

class recipeEditorController(controller):
    mixed_number = re.compile(r'\s*(\d*)\s*(\d[\/]\d)(.*)')
    def __init__(self):
        self.model = KitchenModel.getInstance()

    def setup(self):
        self.ingTableKey = self.model.get("tabData", "-EDITOR-","ingTableKey")
        self.recFields = self.model.get("tabData", "-EDITOR-", "recFields")
        self.ingTable = self.model.get("tabData", "-EDITOR-", "ingTable")

    def handle(self, event, values):
        if event =='-VIEW-RECIPE-':
            # recipe is saved then sent to viewer
            self.saveFields()
            # self.recipe_modal(self.getFields())
            rec = self.getFields()
            self.model.set('activeRecipe', value=rec)
            self.model.set('active_view', value='-VIEWER-')
            return True
        elif event == '-SAVE-RECIPE-':
            self.saveFields()
            return True
        elif event == '-DELETE-RECIPE-':
            if self.model.get('activeRecipe') == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            # delete recipe and return to table view
            self.deleteRecipe()
            self.model.set('active_view', value='-TABLE-')
            return True
        elif event == '-CLEAR-RECIPE-':
            # self.clearFields()
            # print('clear recipe called')
            if self.popup_yes_no('Would you like to save before clearing?', title='Save?'):
                self.saveFields()
            self.model.set('activeRecipe', value=None)
            return True
        elif event == '-INGREDIENT-SBUTTON-':
            self.getIngResults(values['-INGREDIENT-SBOX-'])
            return True
        elif event == '-ADD-INGREDIENT-':
            # print(values)
            amount = values['-AMOUNT-']
            if '/' in amount:
                matcher = recipeEditorController.mixed_number.match(amount)
                whole = float(matcher.group(1)) if len(matcher.group(1)) > 0 else 0
                amount = f'{whole + eval(matcher.group(2))}{matcher.group(3)}'
            try:
                float(amount.split(' ')[0])
            except ValueError:
                sg.PopupError("amount given in incorrect form!")
                return True
            self.addIng(values[self.ingTableKey][0], amount)
            return True
        return False

    def update(self, data):
        self.table = data
        self.ingTable.update(data)

    def fillFields(self, rec):
        """Function that will fill the recipe fields with the recipe data.
        Input:
        rec: recipe object with information to fill fields with
        """
        logger.debug("fill fields callback with:")
        logger.debug(rec)
        self.model.set('activeRecipe', value=rec)
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
            self.model.window[self.recFields[field]].update(value=value)
            # self.model.window.fill({self.recFields[field]: value})

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
            ing = f"('{database.db_clean(choice['description'])}', {choice['fdcId']}, '{amount}')\n"
            self.model.window[self.recFields['Ingredients']].update(value=ing, append=True)

    def clearFields(self):
        """Simple function that clears all the fields in the recipe view"""
        for field in self.recFields:
            if field == "Total Time":
                continue
            # clear the field
            self.model.window[self.recFields[field]].update(value='')

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
            if field == "Total Time":
                res["Total Time"] = res["Prep Time"] + res["Cook Time"]
                continue
            value = self.model.window[self.recFields[field]]
            if field == "Directions":
                # get info
                text = value.get()
                # data preprocessing, three things going on
                # text.split('\n') returns list of lines in textbox
                # list comprehension goes over the list and removes empty strings
                # then the list is stringed
                # res[field] = str([val for val in text.split('\n') if len(val) > 0])
                res[field] = [val for val in text.split('\n') if len(val) > 0]

            elif field == "Ingredients":
                text = value.get()
                # only the first two things happen here
                temp = [val for val in text.split('\n') if len(val) > 0]
                # Additionally, the tuples are interpreted here,
                # then the whole thing is stringified
                res[field] = [recipe.interp(s) for s in temp]
                for ing in res[field]:
                    if len(ing) != 3:
                        sg.PopupError(f'There is an error with the following ingredient, please delete it and re-add it: {ing}', title="Error!")
                        return None
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
        rec = self.getFields()
        if rec == None:
            logger.debug('A NoneType recipe was returned from getfields, aborting saveFields...')
            return
        if self.model.get('RecipeAPI').recipeExists(rec):
            if sg.popup_yes_no("This recipe already exists, do you want to overwrite it?", title="Overwrite?"):
                # save to db
                self.model.get('RecipeAPI').deleteRecipe(rec)
                try:
                    self.model.get('RecipeAPI').saveRecipe(rec)
                except:
                    sg.PopupError('Error occured during saving', title='Error')
                    logger.debug("Unexpected error:", sys.exc_info()[0])
                    return

        elif (self.model.get('activeRecipe') != None): # and (self.model.get('RecipeAPI').recipeExists(self.model.get('activeRecipe'))):
            if sg.popup_yes_no("This recipe already exists, do you want to overwrite it?", title="Overwrite?"):
                # save to db
                self.model.get('RecipeAPI').deleteRecipe(self.model.get('activeRecipe'))
                try:
                    self.model.get('RecipeAPI').saveRecipe(rec)
                except:
                    sg.PopupError('Error occured during saving', title='Error')
                    logger.debug("Unexpected error:", sys.exc_info()[0])
                    return
        else:
            try:
                self.model.get('RecipeAPI').saveRecipe(rec)
            except:
                sg.PopupError('Error occured during saving', title='Error')
                logger.debug("Unexpected error:", sys.exc_info()[0])
                return
        self.model.set('activeRecipe', value=rec)

    def deleteRecipe(self):
        if sg.popup_yes_no("Are you sure you want to delete this recipe?", title="Delete?"):
            self.model.get('RecipeAPI').deleteRecipe(self.model.window[self.recFields['Title']].get())
            self.clearFields()

    # def searchdb(self, query):
    #     row, col = self.recTableDim
    #     # get search results
    #     recs = self.model.get('RecipeAPI').search(query)
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
    #     self.model.set("state", "lastTableAction", value="search", notify=False)
    #     self.model.set("state", "lastSearch", value=query, notify=False)
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
