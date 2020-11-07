from aito.client import AitoClient
import aito.api as aito_api


class AitoConnection:
    def __init__(self, instance_url, api_key):
        self.instance_url = instance_url
        self.api_key = api_key
        self.client = AitoClient(instance_url=self.instance_url, api_key=self.api_key)

    def query(self, query):
        res = aito_api.generic_query(client=self.client, query=query)
        return res

    def recommend(self, rec_query, top=False):
        res = (
            aito_api.recommend(self.client, rec_query.update({"limit": top}))
            if top
            else aito_api.recommend(self.client, rec_query)
        )
        return res
