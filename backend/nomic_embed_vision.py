
import numpy as np
import torch.nn.functional as F
from transformers import AutoModel, AutoImageProcessor
from PIL import Image, ImageFile
import requests
from typing import Any
from llama_index.core.bridge.pydantic import PrivateAttr
from gpt4all import Embed4All

MODEL_PATH = "./resources/models/nomic-embed-vision-v1.5"

"""Install and store nomics-embed-vision model

processor = AutoImageProcessor.from_pretrained("nomic-ai/nomic-embed-vision-v1.5")
vision_model = AutoModel.from_pretrained("nomic-ai/nomic-embed-vision-v1.5", trust_remote_code=True)

processor.save_pretrained("./resources/models/nomic-embed-vision-v1.5")
vision_model.save_pretrained("./resources/models/nomic-embed-vision-v1.5")
"""


class NomicEmbededVison():
    """
    A class used to embed images using a pre-trained model.
    Attributes
    ----------
    _model : Any
        The pre-trained model used for embedding images.
    _processor : Any
        The processor used to preprocess images before embedding.
    Methods
    -------
    __init__(model_path: str = MODEL_PATH, processor_path: str = MODEL_PATH)
        Initializes the NomicEmbededVison with a pre-trained model and processor.
    embed_image(url: str) -> torch.Tensor
        Embeds an image from a given URL and returns the embedding as a torch.Tensor.
    """
    _model: Any = PrivateAttr()
    _processor: Any = PrivateAttr()

    def __init__(self, model_path: str = MODEL_PATH, processor_path: str = MODEL_PATH):
        self._processor = AutoImageProcessor.from_pretrained(processor_path)
        self._model = AutoModel.from_pretrained(model_path, trust_remote_code=True)

    def embed_image(self, url: str) -> np.ndarray:
        image = Image.open(requests.get(url, stream=True).raw)
        inputs = self._processor(images=image, return_tensors="pt")
        outputs = self._model(**inputs)
        embeddings = F.normalize(outputs.last_hidden_state.mean(dim=1))
        return embeddings.detach().numpy()[0]
    
    def embed_PIL_image(self, image: ImageFile) -> np.ndarray:
        inputs = self._processor(images=image, return_tensors="pt")
        outputs = self._model(**inputs)
        embeddings = F.normalize(outputs.last_hidden_state.mean(dim=1))
        return embeddings.detach().numpy()[0]