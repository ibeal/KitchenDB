from config import *

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

def main(**kwargs):
    logger.debug('testRealm.main running...')
    li = "[('BREAD', 544003, '2'), ('JAM', 389529, '3'), ('Peanut butter', 784416, '4')]"
    # print(interp(li))
    print(eval(li))

    inst = "['1. spread jam', '2. spread PB']"
    print(interp(inst))

    logger.debug('testRealm.main finished.')
