from config import *
from containers.recipe import *
from DB.database import *

def main(**kwargs):
    logger.debug('driver.main running...')
    db = database()


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
