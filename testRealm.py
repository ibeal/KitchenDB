from config import *

def main(**kwargs):
    logger.debug('testRealm.main running...')
    response = apiGetByID(566821)
    js = response.json()
    with open('cheese.json', 'w') as f:
        print(json.dumps(js), file=f)

    logger.debug('testRealm.main finished.')
