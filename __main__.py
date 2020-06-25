import driver, sys, testRealm
from config import *


if '-d' in sys.argv:
    # show debug logs
    logging.basicConfig(level=logging.DEBUG)
    logger.debug('Debug mode activated. All debug logs will be shown')
if '-t' in sys.argv:
    # run the test module && exit
    # should be last, any previously set flags will be used
    testRealm.main()
    exit(0)

driver.main()
