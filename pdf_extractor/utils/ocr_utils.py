import torch
from vietocr.tool.config import Cfg
from vietocr.tool.predictor import Predictor


class VietOCR:
    _config = Cfg.load_config_from_name('vgg_transformer')
    _config['device'] = 'cuda:0' if torch.cuda.is_available() else "cpu"
    _instance = Predictor(_config)
    _instance.model.eval()

    @staticmethod
    @torch.no_grad()
    def get_text(image, return_prob=False):
        return VietOCR._instance.predict(image, return_prob)