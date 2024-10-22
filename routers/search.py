from fastapi import FastAPI, HTTPException,Form,APIRouter,UploadFile, File
from fastapi.responses import JSONResponse  
from database.mongodb import MongoDB
from config.config import settings
from pydantic import BaseModel
from PIL import Image
from utils.logger import logger
from service.server import SearchServer
from models.clip_model import get_model
from typing import Union, List
from service.data_workspace_detail_service import find
from utils.utils import base64_to_image,generate_base64_list_image_data
import ast
import asyncio
import os
from utils.client import MongoDBClient
from concurrent.futures import ThreadPoolExecutor

import io 


router = APIRouter() 
collection = MongoDBClient(settings.mongodb_collection)
model = get_model()
server = SearchServer(collection, model)


class SearchImageRequest(BaseModel):
    dataset_id: int
    base64_str: str
    topn: int = 10
    minimum_width: int = 0
    minimum_height: int = 0
    extension_choice: Union[List[str], None] = None


class SearchTextRequest(BaseModel):
    dataset_id: int
    text: str
    topn: int = 10
    minimum_width: int = 0
    minimum_height: int = 0
    extension_choice: Union[List[str], None] = None
    
class ImportResponse(BaseModel):
    success: bool
    data: List[int]
    score: List[float]


@router.post("/image")
def search_image(request: SearchImageRequest):
    """
    Search for images based on the image

    args:
    path: str: The path to the image
    topn: int: The number of images to return 
    minimum_width: int: The minimum width of the image
    minimum_height: int: The minimum height of the image
    extension_choice: list of str: The list of extensions to search for 

    return:
    success: bool: True if the search was successful
    data: list of dict:
        The list of images that matched the search
        The list of scores for each image

    """
    try:
        if request.base64_str is None:
            raise HTTPException(status_code=400, detail="Path is required")
        image = base64_to_image(request.base64_str)
        file_path_list, score_list = server.search_image(image,  request.dataset_id,topn=request.topn, minimum_width=request.minimum_width, minimum_height=request.minimum_height, extension_choice=request.extension_choice)
        # base64_str_list = generate_base64_list_image_data(file_path_list)
        return ImportResponse(success=True,data=file_path_list,score=score_list )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.post("/import/{workspace_id}")
async def upload_data(workspace_id: int):
    """
    import data from workspace to database
    args:

    workspace_id: 

    return:
    success: bool: True if the data was uploaded successfully
    data: list of str: The list of inserted_id of the images
    """
    workspace_id = workspace_id
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="Workspace ID is required") 
    try:
        id_list, file_path_list = find(workspace_id)
        results = await server.import_image_dir(id_list, file_path_list, model, copy=False)
        return results
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/text")
def search_text_by_id(request: SearchTextRequest):
    """
    Search for images based on the text

    """
    try:
        logger.info(f"search_text_by_id: {request.dataset_id}")
        file_path_list, score_list =  server.search_image(request.text, request.dataset_id, topn=request.topn, minimum_width=request.minimum_width, minimum_height=request.minimum_height, extension_choice=request.extension_choice)
        return ImportResponse(success=True,data=file_path_list,score=score_list )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


class UploadImageRequest(BaseModel):
    base64_str: str
    workspace_file_id: int


@router.post("/upload")
def upload_single_image(request: UploadImageRequest):
    """
    Upload a single image to the database

    """
    try:
        result = server.import_image_dir_sync(request.workspace_file_id, request.base64_str, model, copy=False)
        if result is None:
            raise HTTPException(status_code=500, detail="Error uploading image")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
