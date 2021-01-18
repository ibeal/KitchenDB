import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
import KitchenGUI.searchBar as searchBar
from DB.database import *
from containers.recipe import *
from apiCalls import *
from KitchenModel import *
from views.view import view
from controllers.recipeEditorController import *
logger = logging.getLogger('recipeEditor log')

class recipeEditor(sg.Tab, view):
    mixed_number = re.compile(r'\s*([\d\\\/\s]+)(.*)')
    def __init__(self, title, master, *args, ingTableKey = '-OPTION-TABLE-', **kwargs):
        self.model = KitchenModel.getInstance()
        self.master = master
        self.ingTableKey = ingTableKey
        self.recFields = {field: f'-{field}-BOX-' for field in recipe.pretty_fields}
        super().__init__(title, layout=self.layout_init(), *args, **kwargs)

        self.model.addTab("-EDITOR-", self, recipeEditorController(),
            {"recFields":self.recFields,
             "ingTableKey":self.ingTableKey,
             "ingTable":self.ingTable})
        # self.model.set("tabData", "-EDITOR-", value={"recFields":self.recFields, "ingTableKey":self.ingTableKey})
        # self.controller = recipeEditorController(self.recFields, self.ingTableKey)

    def labeledEntry(self,label,key=None,**kwargs):
        box = sg.In(key=f'-{key if key else label}-BOX-',**kwargs)
        return [sg.T(label),box]

    def update(self, data):
        self.table = data
        self.ingTable.update(data)

    def refreshView(self, model, key):
        if key == "activeRecipe":
            if model.get('activeRecipe') == None:
                self.clearFields()
            else:
                self.fillFields(self.model.get('activeRecipe'))
        elif key == "active_view":
            if self.model.get("active_view") == "-EDITOR-":
                self.Select()

    def layout_init(self):
        simpleFields = [field for field in recipe.pretty_fields]
        simpleFields.remove('Ingredients')
        simpleFields.remove('Directions')
        simpleInputs = [
            self.labeledEntry('Title'),
            [
                *self.labeledEntry('Prep Time',size=(5,1)),
                *self.labeledEntry('Cook Time',size=(5,1)),
                *self.labeledEntry('Yield',size=(10,1)),
                *self.labeledEntry('Rating',size=(5,1))
            ],
            [
                *self.labeledEntry('Category',size=(40,1)),
            ],
            [*self.labeledEntry('Source'), sg.Button('AutoFill', key="-AUTOFILL-", disabled=True)]
        ]
        # self.master.recFields = {field: simpleInputs[field][1] for field in simpleFields}


        # data = [['BLANK']*3 for i in range(3)]
        data = []

        self.ingTable = sg.Table(data,
                                num_rows=5,
                                headings=['Food', 'Company', 'Ingredients'],
                                col_widths=[8, 20, 20],
                                auto_size_columns=False,
                                key=self.ingTableKey,
                                enable_events=True)
        # self.master.expands['x'].append(self.ingTable)

        dir = sg.Multiline(key='-Directions-BOX-', size=(50,10))
        # self.master.expands['xy'].append(dir)
        # self.master.recFields['Directions'] = dir

        ing = sg.Multiline(key='-Ingredients-BOX-', size=(50,10))
        # self.master.expands['xy'].append(ing)
        # self.master.recFields['Ingredients'] = ing

        addbox = [sg.T('Amount'), sg.In(key='-AMOUNT-')]
        # self.master.expands['x'].append(addbox)
        self.search = searchBar.searchBar(key='INGREDIENT', api=self.model.get('RecipeAPI'),
                                          interactive=False)
        layout = [
                [sg.Button('Clear',key='-CLEAR-RECIPE-'),
                 sg.Button('Delete Recipe',key='-DELETE-RECIPE-'),
                 sg.Button('View Recipe', key='-VIEW-RECIPE-'),
                 sg.Button('Save',key='-SAVE-RECIPE-')],
                *simpleInputs,
                [sg.T('Directions')],
                [dir],
                [sg.T('Ingredients')],
                [self.search],
                [self.ingTable],
                # [*addbox, sg.Button('Add',key='-ADD-INGREDIENT-')],
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
        logger.debug(rec.title)
        # self.model.set('activeRecipe', value=rec)
        # rec.gets returns a dictionary with all the information in it
        for field, value in rec.guts().items():
            if field == "Directions":
                # data preprocessing, each direction should be seperated with a newline
                value = '\n'.join(value)
                value += '\n'
            elif field == "Ingredients":
                # data preprocessing, each direction is grouped in three and seperated
                # with newlines
                # print(value)
                value = '\n'.join([f'{a,b,c}' for a,b,c in value])
                # value = '\n'.join([f'{ing}' for ing in value])
                value += '\n'
            elif field == "Total Time":
                continue
            # clear the field
            # self.recFields[field].delete(SPOT, tk.END)
            # fill the field
            self.model.window[self.recFields[field]].update(value=value)
            # self.master.window.fill({self.recFields[field]: value})

    def clearFields(self):
        """Simple function that clears all the fields in the recipe view"""
        for field in self.recFields:
            if field == "Total Time":
                continue
            # clear the field
            self.model.window[self.recFields[field]].update(value='')

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
