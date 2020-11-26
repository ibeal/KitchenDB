from recipeCreator import *
from DB.database import *
import logging

def main(**kwargs):
    global logger
    logger = logging.getLogger('Debug Log')
    logger.debug('driver.main running...')
    db = database(returnRecipe=False)

    quit = False
    while quit == False:
        inp = input('What would you like to do? ')
        print()
        inp = inp.lower()
        if inp == 'quit' or inp == 'q':
            quit = True
            break # May be removed depending on how I want to handle quit
        elif inp == 'help':
            print('Available Commands are:')
            print('help -- prints all commands')
            print('add -- opens recipe creator')
            print('show -- prints all recipes in database')
            print('search -- prompts for a query string then returns matches')
        elif inp == 'add':
            db.addNew()
            print()
        elif inp == 'show':
            db.showAll()
            print()
        elif inp == 'search':
            query = input('Database Search: ')
            res = db.search(query)
            if len(res) < 1:
                print('No Results Found\n')
            else:
                for i, row in enumerate(res, 1):
                    print(f'{i})')
                    print(recipe(row))
                    # print(i, row)

                pick = int(input('\nWhich recipe would you like to look at? (number) '))
                rc = recipe(res[pick-1])
        else:
            print('Command not recognized. Type "help" for commands, or "quit" to quit')
            print()

    logger.debug('driver.main finished.')

def getIng():
    """Function that takes user input to build the ingredient list"""
    print('\nNow we will gather the ingredients. Please search for the food item')
    print('quit with "q" or a blank line')
    api = apiCalls()
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
        response = api.apiSearchFood(inp)
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
