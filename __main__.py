import mainCLI, sys, testRealm, logging, mainGui

import KitchenGUI as gui

global logger
logger = logging.getLogger('Debug Log')

if '-d' in sys.argv:
    # show debug logs
    logging.basicConfig(level=logging.DEBUG)
    logger.debug('Debug mode activated. All debug logs will be shown')

if '--cli' in sys.argv:
    mainCLI.main()
    exit(0)

if '-t' in sys.argv:
    # run the test module && exit
    # should be last, any previously set flags will be used
    testRealm.main()
    exit(0)

mainGui.main()
