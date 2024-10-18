from typing import Union, List
from fastapi.responses import JSONResponse
from typing import List, Optional
from fastapi_socketio import SocketManager

from PIL import Image
import io
import ast
from fastapi import FastAPI, HTTPException,Form,WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, APIRouter   
from config.config import settings
from models.clip_model import get_model
from database.mongodb import MongoDB   
from service.server import SearchServer
from routers import search


def lifespan(app: FastAPI):
    app.state.db = MongoDB(settings.mongodb_host, settings.mongodb_port, settings.mongodb_database, settings.mongodb_collection)
    # start to load clip model 
    app.state.model = get_model()

    app.state.db.connect() 

    yield
    # Shutdown: Close database connections and clean up resources
    app.state.db.close()

    
app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.include_router(search.router, prefix="/search", tags=["search"])


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to the API"}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}
    

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level    
    )