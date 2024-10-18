import logging 
from logging.handlers import RotatingFileHandler 
import os 
from fastapi.logger import logger as fastapi_logger



def setup_logging(log_level: str = "INFO", log_file: str = "app.log"):
    # 创建日志目录（如果不存在）
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_file)

    # 配置根日志记录器
    logging.basicConfig(level=log_level)
    logger = logging.getLogger()

    # 创建文件处理程序
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10*1024*1024, backupCount=5)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # 创建控制台处理程序
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # 将处理程序添加到根日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 设置 FastAPI 日志记录器
    fastapi_logger.handlers = logger.handlers
    fastapi_logger.setLevel(log_level)

    return logger

# 创建全局日志记录器实例
logger = setup_logging()