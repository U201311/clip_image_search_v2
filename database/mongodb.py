from pymongo import ReadPreference
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient
from utils.logger import logger
from config.config import settings
import pymongo
from pymongo import MongoClient, ReadPreference


class MongoDB:
    def __init__(self):
        self.mongodb_url = settings.mongodb_url
        self.client = None 
        self.db = None

    def connect(self):
        if not self.client:
            try:
                self.client = MongoClient(self.mongodb_url, 
                    username=settings.mongodb_username,
                    password=settings.mongodb_password,
                    authSource=settings.mongodb_authsource,
                    read_preference=ReadPreference.PRIMARY)
                self.db = self.client[settings.mongodb_database]
                logger.info("MongoDB connection established")
            except Exception as e:
                logger.error(f"MongoDB connection error: {e}")
                raise ConnectionFailure("MongoDB connection error")


    

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

    