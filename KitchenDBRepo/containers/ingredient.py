import logging
logger = logging.getLogger('ingredient object Log')

class ingredient:
    def __init__(self, data=None):
        if data:
            self.edit(data)
        else:
            self.new()

    def edit(self, data):
        pass

    def new(self):
        pass
