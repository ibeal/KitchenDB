import driver, sys, testRealm
from config import *
import KitchenGUI as gui

if '-d' in sys.argv:
    # show debug logs
    logging.basicConfig(level=logging.DEBUG)
    logger.debug('Debug mode activated. All debug logs will be shown')

if '--cli' in sys.argv:
    driver.main()

if '-t' in sys.argv:
    # run the test module && exit
    # should be last, any previously set flags will be used
    testRealm.main()
    exit(0)

gui.main()
