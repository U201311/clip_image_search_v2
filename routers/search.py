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
import ast
import io 


router = APIRouter() 
db = MongoDB(settings.mongodb_host, settings.mongodb_port, settings.mongodb_database, settings.mongodb_collection)
client = db.client
collection = db.get_collection()

model = get_model()
server = SearchServer(collection, model)


class SearchImageRequest(BaseModel):
    path: str
    topn: int = 10
    minimum_width: int = 0
    minimum_height: int = 0
    extension_choice: Union[List[str], None] = None


class SearchTextRequest(BaseModel):
    text: str
    topn: int = 10
    minimum_width: int = 0
    minimum_height: int = 0
    extension_choice: Union[List[str], None] = None


@router.post("/image/")
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
        if request.path is None:
            raise HTTPException(status_code=400, detail="Path is required")
        image = Image.open(request.path)
        result = server.search_image(image, topn=request.topn, minimum_width=request.minimum_width, minimum_height=request.minimum_height, extension_choice=request.extension_choice)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ImportDirRequest(BaseModel):
    data_url: str


@router.post("/image_dir/")
async def upload_data(request: ImportDirRequest):
    """
    Import images from a directory to the database

    args:
    data_url: str: The path to the directory containing the images

    return:
    success: bool: True if the data was uploaded successfully
    data: list of str: The list of inserted_id of the images
    """
    try:
        result  =  await server.import_image_dir(request.data_url, model, copy=False)
        logger.info(f"Data uploaded successfully")
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text/")
def search_text(request: SearchTextRequest):
    """
    Search for images based on the text

    """
    try:
        result =  server.search_image(request.text, topn=request.topn, minimum_width=request.minimum_width, minimum_height=request.minimum_height, extension_choice=request.extension_choice)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
