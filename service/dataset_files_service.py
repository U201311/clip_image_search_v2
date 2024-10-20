from database.mongodb import MongoDB
from config.config import settings
from utils.logger import logger
from utils.client import MongoDBClient


data_workspace_detail = MongoDBClient("dataset_files")

def find(dataset_id: int):
    """
    find image_list by dataset_id

    """
    try:
        collection = data_workspace_detail.get_collection()
        query = {}
        query["dataset_id"] = int(dataset_id)
        cursor = collection.find(query)
        id_list = []
        for doc in cursor:
            id_list.append(doc["id"])
        return id_list           

    except Exception as e:
        logger.error(f"Error finding image_list: {e}")
        return None
