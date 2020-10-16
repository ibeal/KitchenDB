import logging
# import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
import PySimpleGUIQt as sg
import KitchenGUI.searchBar as search
from database import *
from recipeCreator import *
from apiCalls import *

class recipeEditor(sg.Column):

    def __init__(self, master, *args, **kwargs):
        self.master = master
        super().__init__(layout=self.recipeEditor(), *args, **kwargs)

    def labeledEntry(self,label,key=None,**kwargs):
        box = sg.In(key=f'-{key if key else label}-BOX-',**kwargs)
        self.master.expands['x'].append(box)
        return [sg.T(label),box]

    def recipeEditor(self):
        simpleFields = [field for field in recipe.pretty_fields]
        simpleFields.remove('Ingredients')
        simpleFields.remove('Directions')
        simpleInputs = [
            self.labeledEntry('Title'),
            [
                *self.labeledEntry('Prep Time',size=(10,)),
                *self.labeledEntry('Cook Time',size=(10,)),
                *self.labeledEntry('Total Time',size=(5,))
            ],
            [
                *self.labeledEntry('Yield',size=(10,)),
                *self.labeledEntry('Category',size=(10,)),
                *self.labeledEntry('Rating',size=(5,))
            ],
            self.labeledEntry('Source')
        ]
        # self.master.recFields = {field: simpleInputs[field][1] for field in simpleFields}


        # data = [['BLANK']*3 for i in range(3)]
        data = []

        self.ingTable = sg.Table(data,
                                num_rows=5,
                                headings=['Food', 'Company', 'Ingredients'],
                                col_widths=[10, 25, 40],
                                auto_size_columns=False,
                                key='-OPTION-TABLE-')
        self.master.expands['x'].append(self.ingTable)

        dir = sg.Multiline(key='-Directions-BOX-',size=(None,10))
        self.master.expands['xy'].append(dir)
        # self.master.recFields['Directions'] = dir

        ing = sg.Multiline(key='-Ingredients-BOX-',size=(None,10))
        self.master.expands['xy'].append(ing)
        # self.master.recFields['Ingredients'] = ing

        addbox = sg.In('Amount',key='-AMOUNT-')
        self.master.expands['x'].append(addbox)
        layout = [
                [sg.Button('Clear',key='-CLEAR-RECIPE-'),
                 sg.Button('Delete Recipe',key='-DELETE-RECIPE-'),
                 sg.Button('Print Recipe', key='-PRINT-RECIPE-'),
                 sg.Button('Save',key='-SAVE-RECIPE-')],
                *simpleInputs,
                [sg.T('Directions')],
                [dir],
                [sg.T('Ingredients')],
                search.searchBar(self.master, key='INGREDIENT'),
                [self.ingTable],
                [addbox, sg.Button('Add',key='-ADD-INGREDIENT-')],
                [ing]
        ]

        # col = sg.Column(layout=layout,expand_x=True,expand_y=True,justification='center')
        # self.master.expands['xy'].append(col)
        return layout
