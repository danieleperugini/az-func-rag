import os
import pymongo
import dns.resolver

class MongoDbProvider:
    def __init__(self, dbname:str) -> None:
        dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers=['8.8.8.8']
        COSMOS_MONGO_USER = os.environ["cosmos_db_mongo_user"]
        COSMOS_MONGO_PWD = os.environ["cosmos_db_mongo_pwd"]
        COSMOS_MONGO_SERVER = os.environ["cosmos_db_mongo_server"]   
        self.mongo_conn = f"mongodb+srv://{COSMOS_MONGO_USER}:{COSMOS_MONGO_PWD}@{COSMOS_MONGO_SERVER}?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
        self.mongo_client = pymongo.MongoClient(self.mongo_conn)
        self.db = self.mongo_client[dbname]

    def init_db(self, collection:str, drop_collection_if_exists:bool) -> None:
        if (drop_collection_if_exists):
            self.drop_collection(collection=collection)
        self.ensure_collection_exist(collection=collection)

    def drop_collection(self, collection:str) -> None:
        if self.COSMOS_MONGO_COLLECTION in self.db.list_collection_names():
            self.db.drop_collection(collection)

    def ensure_collection_exist(self, collection:str) -> None:
        if collection not in self.db.list_collection_names():
            self.db.create_collection(collection)

    def ensure_vector_index_exist(self, collection:str, field:str):
        INDEX_NAME="VectorSearchIndex"
        index_exists = any(index["name"] == INDEX_NAME for index in self.db[collection].list_indexes())
        if index_exists:
            return
        
        self.db.command({
            'createIndexes': collection,
            'indexes': [{
                'name': INDEX_NAME,
                'key': {
                    field: "cosmosSearch"
                },
                'cosmosSearchOptions': {
                    'kind': 'vector-ivf',
                    'numLists': 1,
                    'similarity': 'COS',
                    'dimensions': 1536
                }
            }]
        })

    def insert_many(self, collection:str, data) -> None:
        collection = self.db[collection]
        collection.insert_many(data)

    def vector_search(self, collection_name:str, field_name:str, query_embedding, num_results=5):
        collection = self.db[collection_name]
        pipeline = [
            {
                '$search': {
                    "cosmosSearch": {
                        "vector": query_embedding,
                        "path": field_name,
                        "k": num_results#, #, "efsearch": 40 # optional for HNSW only 
                        #"filter": {"title": {"$ne": "Azure Cosmos DB"}}
                    },
                    "returnStoredSource": True }},
            {'$project': { 'similarityScore': { '$meta': 'searchScore' }, 'document' : '$$ROOT' } }
        ]
        results = collection.aggregate(pipeline)
        return results