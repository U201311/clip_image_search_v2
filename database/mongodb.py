from pymongo import ReadPreference
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient
from utils.logger import logger
from config.config import settings
import pymongo
from pymongo import MongoClient, ReadPreference


class MongoDB:
    def __init__(self, host: str, port: int, database: str, collection: str):
        self.host = host
        self.port = port
        self.database = database
        self.collection_name = collection
        self.mongodb_url = f"mongodb://{self.host}:{self.port}"
        self.username = settings.mongodb_username
        self.password = settings.mongodb_password
        self.client = None
        self.db = None
    

    def get_collection(self): 
        if not self.client:
            self.connect()
        self.collection = self.client[self.database][self.collection_name]
        return self.collection

    
    
    def insert_one(self, data):
        self.collection.insert_one(data)


    def connect(self):
        try:
            if self.username and self.password:
                self.client = MongoClient(self.mongodb_url, username=self.username, password=self.password)
            else:
                self.client = MongoClient(self.mongodb_url)
                
            self.client.admin.command('ismaster')
            
            # 判断collection是否存在, 不存在则创建 
            if self.collection_name not in self.client[self.database].list_collection_names():
                self.client[self.database][self.collection_name].create_index("id", name="feature_index")
            
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise


    def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed")


    def __aenter__(self):
        self.connect()
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":

    mongo = MongoDB(
        settings.mongodb_host, 
        settings.mongodb_port, 
        settings.mongodb_database, 
        settings.mongodb_collection
    )
    mongo.connect() 
    new_collection_name = "dataset_files"
    new_collection = mongo.client[settings.mongodb_database][new_collection_name]

    

    # async def test_connection():
    #     mongo = MongoDB(
    #         settings.mongodb_host, 
    #         settings.mongodb_port, 
    #         settings.mongodb_database, 
    #         settings.mongodb_collection
    #     )
    #     await mongo.connect()
    #     await mongo.close()

    # asyncio.run(test_connection())