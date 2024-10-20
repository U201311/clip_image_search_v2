import os 
import numpy as np 
from concurrent.futures import ThreadPoolExecutor
import asyncio
import torch 
import shutil 
from datetime import datetime 
from PIL import Image 
from utils.logger import logger
from config.config import settings
from models.model_utils import get_feature_size, cosine_similarity, get_file_type
from models.clip_model import get_model, CLIPModel
from utils.utils import calc_md5, get_full_path
from service import dataset_files_service 



class SearchServer:
    def __init__(self, mongo_collection, model: CLIPModel):
        self.device = settings.device
        self.feat_dim = get_feature_size(settings.clip_model)
        self.mongo_collection = mongo_collection
        
        self.model = model
        self._MAX_SPLIT_SIZE = 8192

    def _get_search_filter(self, args):
        ret = {}
        if len(args) == 0: return ret
        if 'minimum_width' in args:
            ret['width'] = {'$gte': int(args['minimum_width'])}
        if 'minimum_height' in args:
            ret['height'] = {'$gte': int(args['minimum_height'])}
        # if 'extension_choice' in args and len(args['extension_choice']) > 0:
        #     ret['extension'] = {'$in': args['extension_choice']}
        return ret
    
    def search_nearest_clip_feature(self, query_feature, dataset_id, topn=20, search_filter_options={}):
        logger.info(f"search_filter_options: {search_filter_options}")
        mongo_query_dict = self._get_search_filter(search_filter_options)
        id_list = dataset_files_service.find(dataset_id)
        if id_list:
            mongo_query_dict["file_id"] = {"$in": id_list}
        cursor = self.mongo_collection.find(mongo_query_dict)
        filename_list = []
        feature_list = []
        sim_score_list = [] 
        try:
            for doc in cursor:  
                feature_list.append(np.frombuffer(doc["feature"], settings.storage_type))
                filename_list.append(doc["_id"])
                if len(feature_list) >= self._MAX_SPLIT_SIZE:
                    feature_list = np.array(feature_list)
                    sim_score_list.append(cosine_similarity(query_feature, feature_list))
                    feature_list = []
            if len(feature_list) > 0:
                feature_list = np.array(feature_list)
                sim_score_list.append(cosine_similarity(query_feature, feature_list))

            if len(sim_score_list) == 0:
                return [], []
            sim_score = np.concatenate(sim_score_list, axis=0)
            top_n_idx = np.argsort(sim_score)[::-1][:topn]
            top_n_filename = [filename_list[idx] for idx in top_n_idx]
            top_n_score = [float(sim_score[idx]) for idx in top_n_idx]
        except Exception as e:
            logger.error(f"Error searching image: {e}")
            return [], []

        return top_n_filename, top_n_score
    

    def search_image(self, query, dataset_id, topn, minimum_width, minimum_height, extension_choice):
        with torch.no_grad():
            if isinstance(query, str):
                target_feature = self.model.get_text_feature(query) 
            elif isinstance(query, Image.Image):
                image_input = self.model.preprocess(query).unsqueeze(0).to(self.model.device)
                image_feature = self.model.model.encode_image(image_input) 
                target_feature = image_feature.detach().cpu().numpy() 
            else:
                assert False, "Invalid query type"
        
        search_option = {
            "minimum_width": minimum_width,
            "minimum_height": minimum_height,
            "extension_choice": extension_choice,
        }

        filename_list, score_list = self.search_nearest_clip_feature(target_feature, dataset_id, topn=int(topn), search_filter_options=search_option)

        return filename_list, score_list
    
    
    def import_image_dir_sync(self, id, filename: str, model: CLIPModel, copy=False):
        logger.info(f"Importing image: {filename}")
        
        
        image_feature, image_size = model.get_image_feature(filename)
        logger.info(f"Image size: {image_size}")
        if image_feature is None:
            logger.info(f"skip file: {filename}")
            return

        # 这里可以添加将图像特征保存到数据库的逻辑
        document = {
            "file_id": id,
            "height": image_size[0],
            "width": image_size[1],
            "feature": image_feature.tolist(),  # 假设 image_feature 是一个 numpy 数组
            "status":1,
            "created_time": datetime.now(),
        }
        self.collection.insert_one(document)
        logger.info(f"Image imported: {filename}")
    

    async def import_image_dir(self, id_list, file_path_list, model: CLIPModel, copy=False):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            tasks = []
            for id, file_path in zip(id_list, file_path_list):
                file_path = os.path.join(settings.import_image_base, file_path)
                tasks.append(loop.run_in_executor(pool, self.import_image_dir_sync, id, file_path, model, copy))
            results = await asyncio.gather(*tasks)
        return results

    # def _import_image_dir_sync(self, data_url, model, copy):
    #     try:
    #         # 模拟导入过程
    #         image = Image.open(data_url)
    #         image_input = model.preprocess(image).unsqueeze(0).to(model.device)
    #         image_feature = model.model.encode_image(image_input)
    #         print(image_feature.size())
    #         return {"feature_size": image_feature.size()}
    #     except Exception as e:
    #         logger.error(f"Error importing image: {str(e)}")
    #         raise

if __name__ == "__main__":
    import asyncio
    from database.mongodb import MongoDB
    from models.clip_model import get_model
    from config.config import settings
