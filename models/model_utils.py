import os
import json
import hashlib
from functools import lru_cache
from utils.logger import logger
import pymongo
from pymongo.collection import Collection
import clip
import numpy as np 

def get_feature_size(model_name):
    if model_name == "ViT-B/32":
        return 512
    elif model_name == "ViT-L/14":
        return 768
    else:
        raise ValueError("Unknown model")  # TODO: complete this table
    


def cosine_similarity(query_feature, feature_list):
    logger.info(f"query_feature: {query_feature.shape}, feature_list: {feature_list.shape}")
    query_feature = query_feature / np.linalg.norm(query_feature, axis=1, keepdims=True)
    feature_list = feature_list / np.linalg.norm(feature_list, axis=1, keepdims=True)
    sim_score = (query_feature @ feature_list.T)

    return sim_score[0]


def get_file_type(image_path):
    libmagic_output = os.popen("file '" + image_path + "'").read().strip()
    libmagic_output = libmagic_output.split(":", 1)[1]
    if "PNG" in libmagic_output:
        return "png"
    if "JPEG" in libmagic_output:
        return "jpg"
    if "GIF" in libmagic_output:
        return "gif"
    if "PC bitmap" in libmagic_output:
        return "bmp"
    return None

