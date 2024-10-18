from config.config import settings
from database.mongodb import MongoDB

class MongoDBClient:
    def __init__(self, collection, mongodb_url: str=settings.mongodb_url):
        self.mongodb = MongoDB()
        self.client = None
        self.collection = collection

    def get_collection(self):
        if not self.mongodb.client:
            self.mongodb.connect()
        return self.mongodb.client[settings.mongodb_database][self.collection]
    
    