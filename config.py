from libs import *
from apiCalls import *

global logger
logger = logging.getLogger('Debug Log')
APOSREPLACE = ';:'
findApos = re.compile("'")
fillApos = re.compile(APOSREPLACE)
logger.debug('funcs imported')
global dataFields
dataFields = ['name string', 'prep_time integer', 'cook_time integer', 'yield string', 'category string',\
  'rating integer', 'ingredients list', 'directions list']

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

def topLevelSplit(line):
    splits = [-1]
    index = 0
    while index < len(line):
        if line[index] == '[':
            index = line.find(']', index+1)
        elif line[index] == '(':
            index = line.find(')', index+1)
        elif line[index] == ',':
            splits.append(index)
        index += 1
    lines = []
    splits.append(len(line))
    for index in range(len(splits) - 1):
        lines.append(line[splits[index]+1:splits[index+1]])
    logger.debug(f'Split returns: {lines}')
    return lines

def interp(line):
    last = len(line)
    for index in range(last):
        if line[index] == '[':
            return [interp(item) for item in topLevelSplit(line[index+1:line.find(']')])]
        elif line[index] == '(':
            return tuple(interp(item) for item in topLevelSplit(line[index+1:line.find(')')]))
        elif line[index] == "'":
            return str(line[index+1:line.find("'", index+1)])
        elif line[index] == '"':
            return str(line[index+1:line.find('"', index+1)])
        elif line[index].isdigit():
            start = index
            while index < last and line[index].isdigit():
                index+=1
            return int(line[start:index+1])
    return ''
