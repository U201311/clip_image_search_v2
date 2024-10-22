import hashlib
import io
import base64
import numpy as np
from PIL import Image
from utils.logger import logger


def calc_md5(filepath):
    with open(filepath, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(4096)
            if not data:
                break
            md5.update(data)
        return md5.hexdigest()
    

def get_full_path(basedir, basename):
    md5hash, ext = basename.split(".") 
    return "{}/{}/{}/{}".format(basedir, ext, md5hash[:2], basename)


def base64_to_image(base64_str: str) -> np.ndarray:
    """
    将base64编码的图片转换为图像数组

    参数:
    - base64_str (str): base64编码的图片字符串

    返回:
    - np.ndarray: 图像数组
    """
    try:
        # 解码base64字符串
        image_data = base64.b64decode(base64_str)
        # 将字节数据转换为PIL图像
        image = Image.open(io.BytesIO(image_data))
        # 将PIL图像转换为numpy数组
        # image_array = np.array(image)
        return image
    except Exception as e:
        logger.error(f"Failed to convert base64 to image array: {e}")
        return None


def image_array_to_pil(image_array: np.ndarray) -> Image.Image:
    """
    将图像数组转换为PIL图像

    参数:
    - image_array (np.ndarray): 图像数组

    返回:
    - Image.Image: PIL图像对象
    """
    try:
        # 将numpy数组转换为PIL图像
        image = Image.fromarray(image_array)
        return image
    except Exception as e:
        logger.error(f"Failed to convert image array to PIL: {e}")
        return None
    

def generate_base64_image_data(image_path: str) -> str:
    """
    生成base64编码的图片数据
    参数:
    - image_path (str): 图片文件路径
    返回:
    - str: base64编码的图片数据
    """
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_str = base64.b64encode(image_data).decode("utf-8")
            return base64_str
    except Exception as e:
        logger.error(f"Failed to generate base64 image data: {e}")
        return None
    

def generate_base64_list_image_data(image_path_list: list) -> list:
    """
    生成base64编码的图片数据列表
    参数:
    - image_path_list (list): 图片文件路径列表
    返回:
    - list: base64编码的图片数据列表
    """
    base64_list = []
    for image_path in image_path_list:
        base64_str = generate_base64_image_data(image_path)
        base64_list.append(base64_str)
    return base64_list  