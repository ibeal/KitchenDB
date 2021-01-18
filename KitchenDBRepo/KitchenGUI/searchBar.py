import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from KitchenModel import *
logger = logging.getLogger('searchBar Log')

class searchBar(sg.Column):
    def __init__(self, key, api=None, interactive=True, length=40, searchbutton=True, getID=False, **kwargs):
        logger.debug(f'searchBar.__init__ called with key={key}, api={api}, length={length}, kwargs={kwargs}')
        if interactive == True and api == None:
            raise Exception('interactive search bar created with no api')
        self.getID = getID
        self.searchbutton = searchbutton
        self.interactive = interactive
        self.api = api
        self.model = KitchenModel.getInstance()
        self.sbox_key = f'-{key}-SBOX-'
        self.sbutton_key = f'-{key}-SBUTTON-'
        self.stable_key = f"-{key}-STABLE-"
        self.options = None
        super().__init__(layout=self.layout_init(length), **kwargs)

    def layout_init(self, length, *args, **kwargs):
        self.sbox = sg.In(key=self.sbox_key, size=(length,1), enable_events=self.interactive)
        # master.expands['x'].append(sbox)
        self.sbutton = sg.Button('Search',key=self.sbutton_key,visible=self.searchbutton)
        opt = [[''], ['']]
        self.stable = sg.Table(headings=['Options'], values=opt, num_rows=3,
        enable_events=self.interactive, auto_size_columns=False, col_widths=[length],
        key=self.stable_key, hide_vertical_scroll=True, visible=False)
        layout = [
                    [sg.T('Search'), self.sbox, self.sbutton],
                    [self.stable]
                 ]
        return layout

    def handle(self, event, values):
        if not self.interactive:
            return False
        if event == self.sbox_key:
            
            if self.getID:
                self.options = [[opt.getID()] for opt in self.api.search(self.sbox.get())]
            else:
                self.options = [[opt.getName()] for opt in self.api.search(self.sbox.get())]
            self.stable.update(visible=True, values=self.options)
            return True
        elif event == self.stable_key:
            self.sbox.update(value=self.options[values[self.stable_key][0]][0])
            return True
        elif event == self.sbutton_key:
            self.stable.update(visible=False)
            return False
        else:
            self.stable.update(visible=False)
        return False
