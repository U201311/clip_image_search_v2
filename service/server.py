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
        if 'extension_choice' in args and len(args['extension_choice']) > 0:
            ret['extension'] = {'$in': args['extension_choice']}
        return ret
    
    def search_nearest_clip_feature(self, query_feature, topn=20, search_filter_options={}):
        logger.info(f"search_filter_options: {search_filter_options}")
        mongo_query_dict = self._get_search_filter(search_filter_options)
        cursor = self.mongo_collection.find(mongo_query_dict)
        filename_list = []
        feature_list = []
        sim_score_list = [] 
        try:
            for doc in cursor:  
                feature_list.append(np.frombuffer(doc["feature"], settings.storage_type))
                filename_list.append(doc["filename"])
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
    

    def search_image(self, query, topn, minimum_width, minimum_height, extension_choice):
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

        filename_list, score_list = self.search_nearest_clip_feature(target_feature, topn=int(topn), search_filter_options=search_option)

        return filename_list, score_list
    
    def _import_image_dir_sync(self, filename:str, model: CLIPModel, copy=False):
        logger.info(f"Importing image: {filename}") 
        filename = os.path.abspath(filename)
        filetype = get_file_type(filename)
        logger.info(f"File type: {filetype}") 
        if filetype is None:
            logger.info(f"skip file: {filename}")
            return 
        
        image_feature, image_size = model.get_image_feature(filename) 
        if image_feature is None:
            logger.info(f"skip file: {filename}")
            return 
        image_feature = image_feature.astype(settings.storage_type) 

        if copy:
            md5hash = calc_md5(filename)
            new_basename = md5hash + '.' + filetype
            new_full_path = get_full_path(settings.import_image_base, new_basename)

            if os.path.isfile(new_full_path):
                print("duplicate file:", filename)
                return

            shutil.copy2(filename, new_full_path)
            stat = os.stat(new_full_path)
        else:
            stat = os.stat(filename)
            new_full_path = filename

        image_mtime = datetime.fromtimestamp(stat.st_mtime)


        image_datestr = image_mtime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        # save to mongodb
        document = {
            'filename': new_full_path,
            'extension': filetype,
            'height': image_size[1],
            'width': image_size[0],
            'filesize': stat.st_size,
            'create_time': image_datestr,
            'status': 1,
            'feature': image_feature.tobytes(),
        }


        
        insert_result  = self.mongo_collection.insert_one(document)
        logger.info(f"Inserted image: {filename}")
        return str(insert_result.inserted_id)
        
    

    async def import_image_dir(self, image_dir, model: CLIPModel, copy=False):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            tasks = []
            for root, _, files in os.walk(image_dir):
                for file in files:
                    image_path = os.path.join(root, file)
                    tasks.append(loop.run_in_executor(pool, self._import_image_dir_sync, image_path, model, copy))
            
            # 等待所有任务完成
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
