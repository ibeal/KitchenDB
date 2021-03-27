import logging
import re
import json
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
# import KitchenGUI.searchBar as search
from contextlib import suppress
# from DB.database import database
from containers.recipe import recipe
# from apiCalls import apiCalls
from KitchenModel import KitchenModel
from controllers.controller import controller
from containers.ingredient import ingredient
logger = logging.getLogger('recipeEditorController Log')

class recipeEditorController(controller):
    mixed_number = re.compile(r'\s*(\d*)\s*(\d[\/]\d)(.*)')
    def __init__(self):
        self.model = KitchenModel.getInstance()
        self.ingTableKey = None
        self.recFields = None
        self.ingTable = None

    def setup(self):
        self.ingTableKey = self.model.get("tabData", "-EDITOR-","ingTableKey")
        self.recFields = self.model.get("tabData", "-EDITOR-", "recFields")
        self.ingTable = self.model.get("tabData", "-EDITOR-", "ingTable")
        self.recIngKey = self.model.get("tabData", "-EDITOR-", "recIngKey")

    def handle(self, event, values):
        if event =='-VIEW-RECIPE-':
            # recipe is saved then sent to viewer
            try:    
                self.saveFields()
            except:
                sg.PopupError('Check to make sure you have valid title')
                return True
            # self.recipe_modal(self.getFields())
            rec = self.getFields()
            self.model.set('activeRecipe', value=rec)
            self.model.set('active_view', value='-VIEWER-')
            return True
        elif event == '-SAVE-RECIPE-':
            try:    
                self.saveFields()
            except:
                sg.PopupError('Check to make sure you have valid title')
                return True
            return True
        elif event == '-DELETE-RECIPE-':
            if self.model.get('activeRecipe') == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            # delete recipe and return to table view
            self.delete()
            self.model.set('active_view', value='-TABLE-')
            self.model.notifyOberservers()
            return True
        elif event == '-NEW-RECIPE-':
            # self.clearFields()
            # print('clear recipe called')
            if len(self.model.window[self.recFields['Title']].get()) > 0 and\
                 sg.popup_yes_no('Would you like to save before clearing?', title='Save?'):
                self.saveFields()
            self.model.set('activeRecipe', value=recipe())
            return True
        elif event == '-INGREDIENT-SBUTTON-':
            self.getIngResults(values['-INGREDIENT-SBOX-'])
            return True
        elif event == self.recIngKey:
            ing = ingredient(self.model.get(
                'newRecipe').ingredients[values[self.recIngKey][0]])
            self.ingredient_modal(ing)
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
        elif event == self.ingTableKey:
            self.add_ing_modal(values[self.ingTableKey][0])
            self.model.notifyOberservers('newRecipe')
        return False

    def update(self, data):
        self.table = data
        self.ingTable.update(data)

    def ingredient_modal(self, ing):
        layout = [
            [sg.T(ing.name)],
            [sg.In(ing.amount, key='-AMOUNT-'),
             sg.Combo([ing.unit], default_value=ing.unit, key='-UNIT-')],
            [sg.Button('Close', key='-CLOSE-'),
             sg.Button('Update', key='-UPDATE-'),
             sg.Button('Delete', key='-DELETE-')]
        ]

        window = sg.Window('Ingredient Viewer', layout, finalize=True, modal=True)

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "-CLOSE-"):
                break

            elif event == '-DELETE-':
                self.model.get('newRecipe').remove_ing(ing.id)
                self.model.notifyOberservers('newRecipe')
                break

            elif event == '-UPDATE-':
                amount = window['-AMOUNT-']
                unit = window['-UNIT-']
                self.model.get('newRecipe').update_amount(amount=amount, unit=unit)
                break

        window.close()
        
    def add_ing_modal(self, choice):
        choice = self.ingTableData[choice]
        logger.debug(f'choice:{choice}')
        food_info = self.model.get('api').apiGetByID(choice["fdcId"])
        logger.debug(f'food_info:{food_info}')
        serving_size = food_info["householdServingFullText"].split(' ', 1)
        # serving_size = ('2', 'Cups')
        # logger.debug(f'serving_size:{serving_size}')
        # units = [serving_size[1]]
        units = ['tsp', 'Tbsp', 'Cups', serving_size[1]]
        # units.append(serving_size)
        
        layout = [
            [sg.Multiline(choice, size=(50,8))],
            [sg.T('Amount: '),
             sg.In(key='amount-quantity', default_text=serving_size[0], size=(10,1)),
             sg.Combo(values=units, key='amount-unit',
                     default_value=serving_size[1], size=(10,1))],
            [sg.Button('Add', key="-MODAL-ADD-"),
             sg.Button('Cancel', key="-MODAL-CANCEL-")]
        ]

        window = sg.Window('Add Ingredient', layout, finalize=True, modal=True)
        # load active recipe into search bar

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "-MODAL-CANCEL-"):
                break

            elif event == "-MODAL-ADD-":
                amount = window["amount-quantity"].get()
                if '/' in amount:
                    matcher = recipeEditorController.mixed_number.match(amount)
                    whole = float(matcher.group(1)) if len(matcher.group(1)) > 0 else 0
                    amount = whole + eval(matcher.group(2))
                # amount = f'{float(amount)} {window["amount-unit"].get()}'
                ing = ingredient((choice['description'], choice['fdcId'],
                       amount, window["amount-unit"].get()))
                # self.model.get('newRecipe').ingredients.append(ing)
                # self.model.window[self.recFields['Ingredients']].update(value=json.dumps(ing.guts())+'\n', append=True)
                self.model.get('newRecipe').add_ing(ing)
                # self.model.notifyOberservers('activeMenuDay')
                break

        window.close()

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
            # ing = f"('{database.db_clean(choice['description'])}', {choice['fdcId']}, '{amount}')\n"
            ing = (choice["description"], choice['fdcId'], amount)
            self.model.window[self.recFields['Ingredients']].update(value=json.dumps(ing)+'\n', append=True)

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
                # text = value.get()
                # only the first two things happen here

                # temp = [val for val in text.split('\n') if len(val.strip()) > 0]
                # Additionally, the tuples are interpreted here,
                # then the whole thing is stringified

                # res[field] = [ingredient(s) for s in temp]
                res[field] = self.model.get('newRecipe').ingredients

                # for ing in res[field]:
                #     if len(ing) != 3:
                #         sg.PopupError(f'There is an error with the following ingredient, please delete it and re-add it: {ing}', title="Error!")
                #         return None
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
        
        if len(rec.title) <= 0:
            raise Exception("No Title!!!!")           

        if rec is None:
            logger.debug('A NoneType recipe was returned from getfields, aborting saveFields...')
            return
        # case 1: recipe exists, name and source are unchanged
        if self.model.get('RecipeAPI').exists(rec):
            if sg.popup_yes_no("This recipe already exists, do you want to overwrite it?", title="Overwrite?"):
                # save to db
                self.model.get('RecipeAPI').delete(rec)
                try:
                    self.model.get('RecipeAPI').save(rec)
                except Exception as e:
                    sg.PopupError('Error occured during saving', title='Error')
                    logger.debug(f"Unexpected error (case 1): {e}")
                    raise

        # case 2: recipe exists, name and source were changed
        elif (self.model.get('activeRecipe') is not None): # and (self.model.get('RecipeAPI').exists(self.model.get('activeRecipe'))):
            if sg.popup_yes_no("This recipe already exists, do you want to overwrite it?", title="Overwrite?"):
                # save to db
                self.model.get('RecipeAPI').delete(self.model.get('activeRecipe'))
                try:
                    self.model.get('RecipeAPI').save(rec)
                except Exception as e:
                    sg.PopupError('Error occured during saving', title='Error')
                    logger.debug(f"Unexpected error (case 2): {e}")
                    raise
        # case 3: recipe doesn't exist yet
        else:
            try:
                self.model.get('RecipeAPI').save(rec)
            except Exception as e:
                sg.PopupError('Error occured during saving', title='Error')
                logger.debug(f"Unexpected error (case 3): {e}")
                raise
        self.model.set('activeRecipe', value=rec)

    def delete(self):
        if sg.popup_yes_no("Are you sure you want to delete this recipe?", title="Delete?"):
            title = self.model.window[self.recFields['Title']].get()
            source = self.model.window[self.recFields['Source']].get()
            self.model.get('RecipeAPI').delete(name=title, source=source)
            self.clearFields()

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
        options = response['foods']
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
