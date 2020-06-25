from libs import *

apiKey = 'Uk9R497XuT9TaSKdctYsOs9WkpduyKDeoiIJemb0'
apiId = 'https://developer.nrel.gov/fdc/v1/?api_key=k9R497XuT9TaSKdctYsOs9WkpduyKDeoiIJemb0&location=Denver+CO'

def apiGetByID(id):
    """Returns the request item recieved. Format of the .json() of the opject is:
    {
        "fdcId": 45001529,
        "dataType": "Branded",
        "description": "BROCCOLI",
        "foodCode": "string",
        "foodNutrients": [
          {
            "number": 303,
            "name": "Iron, Fe",
            "amount": 0.53,
            "unitName": "mg",
            "derivationCode": "LCCD",
            "derivationDescription": "Calculated from a daily value percentage per serving size measure"
          }
        ],
        "publicationDate": "4/1/2019",
        "scientificName": "string",
        "brandOwner": "Supervalu, Inc.",
        "gtinUpc": "041303020937",
        "ingredients": "string",
        "ndbNumber": "string",
        "additionalDescriptions": "Coon; sharp cheese; Tillamook; Hoop; Pioneer; New York; Wisconsin; Longhorn",
        "allHighlightFields": "string",
        "score": 0
      }
      """
    return rq.get(f'https://api.nal.usda.gov/fdc/v1/food/{id}?api_key={apiKey}')

def apiGetFoodList():
    """Returns a list of all food items. Format of the .json() of the object is:
    Unknown
    """
    return rq.get(f'https://api.nal.usda.gov/fdc/v1/foods/list?api_key={apiKey}')

def apiSearchFood(searchStr, **params):
    """Returns a list of all food items. Format of the .json() of the object is:
    {
    "foodSearchCriteria": {},
    "totalHits": 1034,
    "currentPage": 0,
    "totalPages": 0,
    "foods": [
      {
        "fdcId": 45001529,
        "dataType": "Branded",
        "description": "BROCCOLI",
        "foodCode": "string",
        "foodNutrients": [
          {
            "number": 303,
            "name": "Iron, Fe",
            "amount": 0.53,
            "unitName": "mg",
            "derivationCode": "LCCD",
            "derivationDescription": "Calculated from a daily value percentage per serving size measure"
          }
        ],
        "publicationDate": "4/1/2019",
        "scientificName": "string",
        "brandOwner": "Supervalu, Inc.",
        "gtinUpc": "041303020937",
        "ingredients": "string",
        "ndbNumber": "string",
        "additionalDescriptions": "Coon; sharp cheese; Tillamook; Hoop; Pioneer; New York; Wisconsin; Longhorn",
        "allHighlightFields": "string",
        "score": 0
      }
    ]
  }
  """
    for k,v in params:
        searchStr += f'{k}: {v}'
    return rq.get(f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={apiKey}&query={searchStr}')
