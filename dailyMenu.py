import logging
logger = logging.getLogger('recipeTableController Log')

class dailyMenu:
    def __init__(self, date):
        self.date = date
        # self.name = date
        # if name:
        #     self.name = name
        self.shopping = []
        self.data = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snacks': []
        }

    def add_category(self, group):
        if group in self.data.keys():
            logger.debug('Tried Adding group that already exists')
        else:
            self.data[group] = []

    def add(self, group, rec):
        if group.lower() in ['breakfast']:
            self.data.breakfast.append(rec)
        elif group.lower() in ['lunch']:
            self.data.lunch.append(rec)
        elif group.lower() in ['dinner']:
            self.data.dinner.append(rec)
        elif group.lower() in ['snacks']:
            self.data.snacks.append(rec)
        elif group.lower() in self.data.keys():
            self.data[group].append(rec)
        else:
            logger.debug("group not supported")
            raise Exception(f"Unsupported group given {group}")
