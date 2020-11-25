import mainGui
import KitchenGUI
import logging
from KitchenModel import *


def main(**kwargs):
    global logger
    logger = logging.getLogger('Debug Log')
    logger.debug('testRealm.main running...')
    model = KitchenModel.getInstance()
    model.seta("views", "-INVENTORY-", value="Test")
    print(model.get("views"))

    logger.debug('testRealm.main finished.')
