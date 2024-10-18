import json
from pydantic_settings import BaseSettings

from pydantic import  Field, SecretStr
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    # mongodb 配置
    mongodb_host: str = Field(default="127.0.0.1", alias="mongodb-host")
    mongodb_port: int = Field(default=27017, alias="mongodb-port")
    mongodb_database: str = Field(default="db", alias="mongodb-database")
    mongodb_collection: str = Field(default="images", alias="mongodb-collection")

    
    mongodb_username: str = Field(default=None, alias="mongodb-username")
    mongodb_password: str = Field(default=None, alias="mongodb-password")


    # 设备配置
    device: str = Field(default="cpu", alias="device")
    storage_type: str = Field(default="float32", alias="storage-type")
    
    # CLIP 模型配置
    clip_model: str = Field(default="ViT-B/32", alias="clip-model")
    clip_model_download: str = Field(default="./models", alias="clip-model-download")
    import_image_base: str = Field(default="./data", alias="import-image-base")
    
    # OCR 配置
    enable_ocr: bool = Field(default=False, alias="enable-ocr")
    ocr_det_model: str = Field(default="ch_PP-OCRv3_det_infer", alias="ocr-det-model")
    ocr_rec_model: str = Field(default="ch_PP-OCRv3_rec_infer", alias="ocr-rec-model")
    ocr_model_download: str = Field(default="./models", alias="ocr-model-download")


    # log 配置
    log_level: str = Field(default="info", alias="log-level")
    log_file: str = Field(default="logs/app.log", alias="log-file")


    @classmethod
    def from_json(cls, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return cls(**config_data)

# 获取当前文件的目录
base_dir = Path(__file__).resolve().parent.parent
config_path = base_dir / "config.json"

# 从 config.json 文件加载配置
settings = Settings.from_json(config_path)

# 打印配置以验证
print(settings)