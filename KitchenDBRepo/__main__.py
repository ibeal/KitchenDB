#!/usr/bin/env python3

import sys, testRealm, logging, mainGui, os
import tkinter
import KitchenGUI as gui

logger = logging.getLogger('Debug Log')

if '-d' in sys.argv:
    # show debug logs
    logging.basicConfig(level=logging.DEBUG)
    logger.debug('Debug mode activated. All debug logs will be shown')
else:
    # send debug logs to logfile
    logging.basicConfig(level=logging.DEBUG,
                 filename="logfile", filemode="a+")
    logger.debug('Debug logs send to logfile')
    

# if '--cli' in sys.argv:
#     mainCLI.main()
#     exit(0)

if '-t' in sys.argv:
    # run the test module && exit
    # should be last, any previously set flags will be used
    testRealm.main()
    exit(0)

mainGui.main(
    screen_size=(1440,900),
    android=bool('ANDROID_ROOT' in os.environ)
)
