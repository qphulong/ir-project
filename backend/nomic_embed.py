from typing import Any, Coroutine, List
from llama_index.core.base.embeddings.base import Embedding
from llama_index.core.embeddings import BaseEmbedding
from sentence_transformers import SentenceTransformer
from llama_index.core.bridge.pydantic import PrivateAttr
from gpt4all import Embed4All
from transformers import AutoTokenizer, AutoModel, AutoImageProcessor
import torch.nn.functional as F
import torch
import numpy as np

from typing import List

class NomicEmbed(BaseEmbedding):
    """ Code to download model
    model_name = "nomic-ai/nomic-embed-text-v1.5"
    tokenizer = AutoTokenizer.from_pretrained(model_name,trust_remote_code=True)
    model = AutoModel.from_pretrained(model_name,trust_remote_code=True)
    save_directory = ".resources/models/nomic-text-embed-v1.5"
    tokenizer.save_pretrained(save_directory)
    model.save_pretrained(save_directory)
    """

    """
    Class to embed text to embeddings.
    This class inherited with llama_index BaseEmbedding to
    work with this lib components. See BaseEmbedding class

    Attribute:
        _tokenizer (AutoTokenizer):
        _text_model (AUtoModel):

    Methods:
        Well, the function names are self-explained. :)
    """
    _tokenizer = PrivateAttr()
    _text_model = PrivateAttr()
    def __init__(self,model_path:str='./resources/models/nomic-embed-text-v1.5',**kwargs:Any):
        super().__init__(**kwargs)
        self._tokenizer = AutoTokenizer.from_pretrained(model_path)
        self._text_model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        self._text_model.eval()

    def mean_pooling(self,model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def _get_embeddings_for_image_query(self,text:str) -> np.ndarray:
        """Text is directly embed without prefix"""
        encoded_input = self._tokenizer([text], padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = self._text_model(**encoded_input)
        text_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        text_embeddings = F.layer_norm(text_embeddings, normalized_shape=(text_embeddings.shape[1],))
        text_embeddings = F.normalize(text_embeddings, p=2, dim=1)
        text_embeddings = text_embeddings.detach().numpy()
        text_embeddings = text_embeddings[0]
        return text_embeddings

    def _get_text_embedding(self, text:str) -> np.ndarray:
        encoded_input = self._tokenizer([text], padding=True, truncation=True, return_tensors='pt')
        matryoshka_dim = 768
        with torch.no_grad():
            model_output = self._text_model(**encoded_input)
        text_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        text_embeddings = F.layer_norm(text_embeddings, normalized_shape=(text_embeddings.shape[1],))
        text_embeddings = text_embeddings[:, :matryoshka_dim]
        text_embeddings = F.normalize(text_embeddings, p=2, dim=1)
        text_embeddings = text_embeddings.detach().numpy()
        text_embeddings = text_embeddings[0]
        return text_embeddings

    async def _aget_text_embedding(self, text:str)-> np.ndarray:
        embeddings = await self._get_text_embedding(text)
        return embeddings
    
    def _get_query_embedding(self, query: str)-> np.ndarray:
        """dont use"""
        query = 'search_query: ' + query
        encoded_input = self._tokenizer([query], padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = self._text_model(**encoded_input)
        text_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        text_embeddings = F.layer_norm(text_embeddings, normalized_shape=(text_embeddings.shape[1],))
        text_embeddings = F.normalize(text_embeddings, p=2, dim=1)
        text_embeddings = text_embeddings.detach().numpy()
        text_embeddings = text_embeddings[0]
        return text_embeddings
    
    async def _aget_query_embedding(self, query: str)-> np.ndarray:
        embeddings = await self._get_query_embedding(query)
        return embeddings
    
    
class NomicEmbedQuantized(BaseEmbedding):
    """
    BaseEmbedding class interface works with Nomic embed quantized model.
    """
    _embed_model:Embed4All = PrivateAttr()
    def __init__(
            self,
            model_path:str='./resources/models/',
            model_name:str='nomic-embed-text-v1.5.Q8_0.gguf',
            **kwargs:Any
        ):
        super().__init__(**kwargs)
        self._embed_model =  Embed4All(
            model_path=model_path,
            allow_download=False,
            model_name=model_name
        )

    def _get_text_embedding(self, text:str):
        embeddings = self._embed_model.embed(
            text=text,
            prefix='search_document'
        )
        return embeddings

    async def _aget_text_embedding(self, text:str):
        embeddings = await self._embed_model.embed(
            text=text,
            prefix='search_document'
        )
        return embeddings
    
    def _get_query_embedding(self, query: str):
        embeddings = self._embed_model.embed(
            text=query,
            prefix='search_query'
        )
        return embeddings
    
    async def _aget_query_embedding(self, query: str):
        embeddings = await self._embed_model.embed(
            text=query,
            prefix='search_query'
        )
        return embeddings