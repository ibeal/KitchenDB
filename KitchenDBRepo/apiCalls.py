import requests as rq
import logging
logger = logging.getLogger('apiCalls')
import usda

class apiCalls():
    def __init__(self,
                 key='Uk9R497XuT9TaSKdctYsOs9WkpduyKDeoiIJemb0',
                 id='https://developer.nrel.gov/fdc/v1/?api_key=k9R497XuT9TaSKdctYsOs9WkpduyKDeoiIJemb0&location=Denver+CO'):
        self.apiKey = key
        self.apiId = id
        self.api = usda.UsdaClient(key)

    def apiGetByID(self, id):
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
        return rq.get(f'https://api.nal.usda.gov/fdc/v1/food/{id}?api_key={self.apiKey}').json()
        # return self.api.get_food_report(id)

    def apiGetFoodList():
        """Returns a list of all food items. Format of the .json() of the object is:
        Unknown
        """
        return rq.get(f'https://api.nal.usda.gov/fdc/v1/foods/list?api_key={self.apiKey}')

    def apiSearchFood(self, searchStr, limit=20, **params):
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
        return rq.get(f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={self.apiKey}&query={searchStr}').json()
        # return self.api.search_foods_raw(searchStr, limit)
