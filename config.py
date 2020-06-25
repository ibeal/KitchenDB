from libs import *
from apiCalls import *

global logger
logger = logging.getLogger('Debug Log')
APOSREPLACE = ';:'
findApos = re.compile("'")
fillApos = re.compile(APOSREPLACE)
logger.debug('funcs imported')

def aposFilter(dirty):
    """A function that takes a string and replaces all apostrophes with the global
    APOSREPLACE value, currently ';:'. Inverse of aposFiller."""
    if not isinstance(dirty, str):
        logger.debug(f'{dirty} is not a string. aposFilter aborting...')
        return dirty
    clean = findApos.sub(APOSREPLACE, dirty)
    return clean

def aposFiller(clean):
    """A function that takes a string and replaces all instances of COMMAREPLACE,
    currently ';:', with an apostrophe. Inverse of aposFilter."""
    if not isinstance(clean, str):
        logger.debug(f'{clean} is not a string. aposFiller aborting...')
        return clean
    dirty = fillApos.sub("'", clean)
    return dirty
