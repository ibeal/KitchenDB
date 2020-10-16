import csv, json, yaml, sys, logging, re
import sqlite3 as sql
import requests as rq
from contextlib import suppress
global logger

class recipe:
    dataFields = ['name string', 'prep_time integer', 'cook_time integer', 'yield string', 'category string',\
      'rating integer', 'ingredients list', 'directions list', 'source string']
    # fields = ['Title', 'Prep Time', 'Cook Time', 'Yield', 'Category', 'Rating', 'Source',]
    pretty_fields = ['Title', 'Prep Time', 'Cook Time', 'Total Time','Yield', 'Category', 'Rating', 'Ingredients', 'Directions', 'Source']
    def __init__(self, data=None):
        if not data:
            self.new()
        else:
            self.edit(data)

    def __str__(self):
        ingr = ''
        dir = ''
        info = f'{self.name}\nYields: {self.yieldAmnt} | Category: {self.category} | Rating: {self.rating}\n' +\
            f'Time - Prep: {self.prep_time} | Cook: {self.cook_time} | Total: {self.prep_time + self.cook_time}'
        for food, id, amount in self.ingredients:
            ingr += f'{food}: {amount}\n'
        for direction in self.directions:
            dir += f'{direction}\n'

        return f'{info}\n\n{ingr}\n{dir}'

    def guts(self):
        return {"Title": self.name,
                "Prep Time": self.prep_time,
                "Cook Time": self.cook_time,
                "Total Time": self.total_time,
                "Yield": self.yieldAmnt,
                "Category": self.category,
                "Rating": self.rating,
                "Ingredients": self.ingredients,
                "Directions": self.directions,
                "Source": self.source}

    def meta(self):
        return tuple(recipe.pretty_fields)

    def edit(self, data):
        """Function that builds the recipe object from DB entry.
        expects data in this format:
        [('Peanut Butter Sandwich', 5, 0, '1 Sandwich', 'Lunch', -1,
          "[('BREAD', 473832, '2 Slices'), ('Peanut butter', 784416, '3 T'),
              ('JAM', 389529, '3 T')]",
          "['1. Spread PB on Sandwich', '2. Spread Jam on Sandwich', '3. Enjoy!']",
        '')]"""

        if isinstance(data, list) or isinstance(data, tuple):
            self.name = data[0]
            self.prep_time = int(data[1])
            self.cook_time = int(data[2])
            self.total_time = self.prep_time + self.cook_time
            self.yieldAmnt = data[3]
            self.category = data[4]
            self.rating = int(data[5])
            self.ingredients = self.interp(data[6])
            self.directions = self.interp(data[7])
            self.source = data[8]
        elif isinstance(data, dict):
            self.name = data['Title']
            self.prep_time = int(data['Prep Time'])
            self.cook_time = int(data['Cook Time'])
            self.total_time = self.prep_time + self.cook_time
            self.yieldAmnt = data['Yield']
            self.category = data['Category']
            self.rating = int(data['Rating'])
            self.ingredients = self.interp(data['Ingredients'])
            self.directions = self.interp(data['Directions'])
            self.source = data['Source']

    def new(self):
        """Function that builds the recipe.yaml file from user input"""
        self.name = input('Please enter the recipe name: ')
        if self.name == 'q':
            exit()
        # FIXME: error checking on input
        self.prep_time = int(input('Please enter the prep time (minutes): '))
        self.cook_time = int(input('Please enter the cook time (minutes): '))
        self.total_time = self.prep_time + self.cook_time
        self.yieldAmnt = input('Please enter the yield for this recipe: ')
        self.category = input('Please enter the category for this recipe: ')
        self.rating = -1 # unrated
        self.ingredients = getIng()
        self.directions = getDir()
        self.source = input('Add a source, or leave blank: ')
        # self.outputToYaml()

    def outputToYaml(self, filename='recipe.yaml'):
        """function that generates a recipe.yaml file from given parameters"""
        tabfields = ''
        for v in recipe.dataFields:
            tabfields += f'{v}, '
        tabfields = tabfields[:-2]
        yam = {'tabname': 'recipes', \
                'tabfields': tabfields,\
                  'fields': [self.name, self.prep_time, self.cook_time, self.yieldAmnt, self.category, self.rating, str(self.ingredients), str(self.directions), self.source]
                }
        with open(filename,'a') as f:
            f.truncate(0) # clear file
            f.write('---\n')
            yaml.dump(yam, f)
            logger.debug(f'Output to Yaml completed. File: {filename}')

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

        # this iterates through each character, so last is the last character
        last = len(line)
        for index in range(last):
            # if the character is open bracket, we've started a list
            if line[index] == '[':
                # recursive call, returns a list of everything between the open bracket to close bracket
                return [recipe.interp(item) for item in recipe.topLevelSplit(line[index+1:line.find(']')])]
            # if the character is close bracket, we've started a tuple
            elif line[index] == '(':
                # recursive call, returns a tuple of everything between the open paren to close paren
                return tuple(recipe.interp(item) for item in recipe.topLevelSplit(line[index+1:line.find(')')]))
            # if the character is an apostrophe, we have a string
            elif line[index] == "'":
                # return the string of everything in between
                return str(line[index+1:line.find("'", index+1)])
            # if the character is an quotation, we have a string
            elif line[index] == '"':
                # return the stirng of everything in between
                return str(line[index+1:line.find('"', index+1)])
            # if the character is a number, we've started a number
            elif line[index].isdigit():
                start = index
                # continue until the digits end
                while index < last and line[index].isdigit():
                    index+=1
                # return the int of the digits
                return int(line[start:index+1])
        # if we reach the end, we return empty string
        return ''

    @staticmethod
    def getIng():
        """Function that takes user input to build the ingredient list"""
        print('\nNow we will gather the ingredients. Please search for the food item')
        print('quit with "q" or a blank line')
        ingredients = []
        ingNum = 1
        while True:
            inp = input(f'\tPlease enter ingredient {ingNum}: ')
            if inp.lower() == 'q':
                logger.debug('Quiting...')
                break
            elif len(inp) == 0:
                logger.debug('Quiting...')
                break
            response = apiSearchFood(inp)
            options = response.json()['foods']
            upperLimit = len(options) - 1
            min, max = -5,0
            while True:
                if max + 5 > upperLimit - 1:
                    logger.debug('Upper Limit hit')
                    max = upperLimit
                    if max - 5 >= 0:
                        min = max - 5
                    else:
                        min = 0
                else:
                    min += 5
                    max += 5
                for i in range(min, max):
                    with suppress(KeyError):
                        print(f'\tOption {i+1}:')
                        print(f'\t{options[i]["description"]}')
                        if options[i]['dataType'] == 'Branded':
                            print(f'\t{options[i]["brandOwner"]}')
                            print(f'\t{options[i]["ingredients"]}')
                        else:
                            print(f'\t{options[i]["additionalDescriptions"]}')
                    print()

                choice = input('\t(press <Enter> for more choices, enter <discard> to search again)\n\tWhich choice looks best? ').lower()
                if len(choice) < 1:
                    continue
                elif choice[0] == 'p':
                    min = (int(choice[1:]) * 5) - 5
                    max = min + 5
                    logger.debug(f'Page Option:Showing options {min+1} to {max+1}...')
                elif choice[0] == 'd':
                    logger.debug('Discard Option: Discard previous search...')
                    ingNum -= 1
                    break
                while isinstance(choice, str):
                    try:
                        choice = int(choice)
                    except ValueError:
                        print('\tInvalid Choice, Please try again')
                        choice = input('\tWhich choice looks best? (press <Enter> for more choices) ')

                if 1 <= choice <= max:
                    amount = input('\tHow much of the ingredient does the recipe call for? ')
                    amount = aposFilter(amount)
                    print()
                    food = (aposFilter(options[choice-1]['description']), options[choice-1]['fdcId'], amount)
                    ingredients.append(food)
                    logger.debug(f'Successfully add {food} to ingrdients')
                    break
            ingNum += 1
        return ingredients

    @staticmethod
    def getDir():
        """Function that asks for user input to build the direction list"""
        directions = []
        dirNum = 1
        print('\nNow we will gather the directions. Please enter the directions')
        print('quit with "q" or a blank line')
        while True:
            inp = input(f'\tPlease enter step number {dirNum}: ')
            if inp.lower() == 'q':
                logger.debug('Quiting...')
                break
            elif len(inp) < 1:
                logger.debug('Quiting...')
                break
            else:
                directions.append(f'{dirNum}. {inp}')
                dirNum += 1
                logger.debug(f'Successfully added "{inp}" to directions')
        return directions


if __name__ == "__main__":
    # with open('recipes.yaml') as f:
    #     yam = yaml.load(f,Loader=yaml.FullLoader)
    # inyam = yam['fields']
    # outputToYaml(inyam['name'],inyam['prep_time'],inyam['cook_time'],inyam['yield'],\
    # inyam['ingredients'],inyam['directions'],inyam['rating'])
    # getIng()
    pass

"""
fields as a dictionary
'fields': {\
    'name': name,\
    'prep_time': prep_time,\
    'cook_time': cook_time,\
    'yield': yieldAmnt,\
    'ingredients': ingredients,\
    'directions': directions,\
    'rating': rating
    }
"""
