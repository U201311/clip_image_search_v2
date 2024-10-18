from database.mongodb import MongoDB
from config.config import settings
from utils.logger import logger
from utils.client import MongoDBClient


data_workspace_detail = MongoDBClient("data_workspace_detail")

def find(workspace_id: int):
    """
    find image_list by workspace_id

    """
    try:
        collection = data_workspace_detail.get_collection()
        query = {}
        query["workspace_id"] = int(workspace_id)
        cursor = collection.find(query)
        id_list = []
        file_path_list = []
        for doc in cursor:
            id_list.append(doc["_id"])
            file_path_list.append(doc["file_path"])
        return id_list, file_path_list           

    except Exception as e:
        logger.error(f"Error finding image_list: {e}")
        return None
    

    
        
        