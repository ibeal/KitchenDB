import mainGui
import KitchenGUI
import KitchenGUI.table as table
import logging



def main(**kwargs):
    global logger
    logger = logging.getLogger('Debug Log')
    logger.debug('testRealm.main running...')
    table.main()

    logger.debug('testRealm.main finished.')
