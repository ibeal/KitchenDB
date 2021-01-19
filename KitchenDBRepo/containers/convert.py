import json

class convert:
    """Class that provides a way to interpret stings into json objects"""
    @staticmethod
    def topLevelSplit(line):
        """Helper function for interp, splits on every comma that is on the top level.
        any commas that are nested within parens or brackets are skipped"""
        # list of the locations of the commas
        # preloaded with a -1 which resolves to location 0 in the end
        splits = [-1]
        # iterate through each character
        index = 0
        while index < len(line):
            # if we have a open bracket, skip to the closing bracket
            if line[index] == '[':
                index = line.find(']', index+1)
            # if we have a open paren, skip to the closing paren
            elif line[index] == '(':
                index = line.find(')', index+1)
            elif line[index] == '{':
                index = line.find('}', index+1)
            elif line[index] == '"':
                index = line.find('"', index+1)
            elif line[index] == "'":
                index = line.find("'", index+1)
            # if we have a comma, record the location
            elif line[index] == ',':
                splits.append(index)
            # increment to next character
            index += 1

        # list of the different splits
        lines = []
        # add the last location to the end
        splits.append(len(line))

        # for n - 1 splits
        for index in range(len(splits) - 1):
            # record the string from current index + 1 to the next index
            # this way commas are ignored
            start = splits[index]+1
            end = splits[index+1]
            lines.append(line[start:end])
        # logging.debug(f'Split returns: {lines}')
        return lines

    @staticmethod
    def interp(line):
        """Fairly complicated function, used to interpret my stringified list
        it takes a string and outputs a list"""
        if not isinstance(line, str):
            return line
        # this iterates through each character, so last is the last character
        # last = len(line)
        # for index in range(last):
        #     # if the character is open bracket, we've started a list
        #     if line[index] == '[':
        #         # recursive call, returns a list of everything between the open bracket to close bracket
        #         return [convert.interp(item) for item in convert.topLevelSplit(line[index+1:line.find(']')])]
        #     # if the character is close bracket, we've started a tuple
        #     elif line[index] == '(':
        #         # recursive call, returns a tuple of everything between the open paren to close paren
        #         return tuple(convert.interp(item) for item in convert.topLevelSplit(line[index+1:line.find(')')]))
        #     # if the character is close bracket, we've started a tuple
        #     elif line[index] == '{':
        #         # recursive call, returns a tuple of everything between the open paren to close paren
        #         return dict((item.split(':')[0],convert.interp(":".join(item.split(':')[1:]))) for item in convert.topLevelSplit(line[index+1:line.find('}')]))
        #     # if the character is an apostrophe, we have a string
        #     elif line[index] == "'":
        #         # return the string of everything in between
        #         return str(line[index+1:line.find("'", index+1)])
        #     # if the character is an quotation, we have a string
        #     elif line[index] == '"':
        #         # return the stirng of everything in between
        #         return str(line[index+1:line.find('"', index+1)])
        #     # if the character is a number, we've started a number
        #     elif line[index].isdigit():
        #         start = index
        #         # continue until the digits end
        #         while index < last and line[index].isdigit():
        #             index += 1
        #         # return the int of the digits
        #         return int(line[start:index+1])
        # if we reach the end, we return empty string
        line = line.replace("\'", '\"')
        return json.loads(line)

    def __init__(self):
        pass
