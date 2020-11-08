import pandas as pd
import numpy as np
from aito.schema import AitoStringType, AitoTextType, AitoDelimiterAnalyzerSchema, AitoTableSchema, AitoColumnLinkSchema, AitoDatabaseSchema
from aito.client import AitoClient
import aito.api as aito_api


# aito credentials
AITO_INSTANCE_URL = 'https://team1junction.aito.app'
AITO_API_KEY = 'l9uG4dc5ha7BoqBcgT58S2Z7G7uq75ES9w6scxTM'

# define a client to access to the dataset
client = AitoClient(instance_url=AITO_INSTANCE_URL, api_key=AITO_API_KEY)


# query definition
query = {
    "from": "places",
    "where" : {
        "cuisine" : {
            "$match" : "Italian"
        }
    }
}

# send the query
res = aito_api.generic_query(client=client, query=query)
#print(res.to_json_string(indent=2))

# query
rec_query = {
    "from": "ratings",
    "where": {
        "userID": {
            "$or": [
                {"userID": "U1022"},
                {"userID": "U1026"},
                {"userID": "U1024"},
                {"userID": "U1025"},
            ]
        }
    },
    "recommend": "placeID",
    "goal" : {"rating" : 2},
    "limit": 10,
}

# send query
res = aito_api.recommend(client=client, query=rec_query)
#res.json

hits = res.json['hits']
names = []
for h in hits:
    names.append(h["name"])
#names

