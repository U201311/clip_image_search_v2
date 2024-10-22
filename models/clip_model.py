import time 
from functools import lru_cache 
from utils.logger import logger
from PIL import Image 
import torch
import clip 

from config.config import settings

class CLIPModel():
    def __init__(self, config):
        self.config = config
        if config.device == 'cpu':
            self.device = 'cpu'
        else:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model, self.preprocess = self.get_model()

    def get_model(self):
        args = {}
        print(self.device)
        if self.config.clip_model_download is not None:
            args['download_root'] = self.config.clip_model_download
        return clip.load(self.config.clip_model, device=self.device, **args)
    
    def get_image_feature(self, image: Image.Image):
        try:
            # image = Image.open(image_path)
            image_size = image.size 
            image = self.preprocess(image).unsqueeze(0).to(self.device)
        except Exception as e:
            print(e)
            return None, None
        
        with torch.no_grad():
            feat = self.model.encode_image(image)
            feat = feat.detach().cpu().numpy() 
        return feat, image_size
    
    def get_text_feature(self, text):
        text = clip.tokenize([text]).to(self.device)
        with torch.no_grad():
            feat = self.model.encode_text(text)
            feat = feat.detach().cpu().numpy()
        return feat  
    

@lru_cache(maxsize=1)
def get_model() -> CLIPModel:
    config = settings
    _time_start = time.time()
    model = CLIPModel(config) 
    _time_end = time.time() 
    logger.info(f"Model loaded in {_time_end - _time_start} seconds.")
    return model


if __name__ == "__main__":
    model = get_model() 
    print(model.config)


         
        