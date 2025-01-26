import os
from pymongo.mongo_client import MongoClient
from pymongo.database import Database
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

class MongoDBConnection:
    
    def __init__(self, uri: str = None):
        self.uri = uri or os.getenv("MONGO_CONNECTION_STRING")
        self.connection = MongoClient(
            self.uri, 
            server_api=ServerApi('1'),
            maxPoolSize=100,
            minPoolSize=10,
            maxIdleTimeMS=45000,
            retryWrites=True,
        )
        self.database = self.connection[os.getenv("MONGO_DATABASE")]

    def close(self):
        if self.connection:
            self.connection.close()

def get_db() -> Database:
    return MongoDBConnection().database

def get_collection(collection_name: str):
    return MongoDBConnection().database[collection_name]

