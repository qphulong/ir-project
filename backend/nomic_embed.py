from typing import Any, Coroutine, List
from llama_index.core.base.embeddings.base import Embedding
from llama_index.core.embeddings import BaseEmbedding
from sentence_transformers import SentenceTransformer
from llama_index.core.bridge.pydantic import PrivateAttr
from gpt4all import Embed4All

from typing import List

class NomicEmbed(BaseEmbedding):
    """
    Class to embed text to embeddings.
    This class inherited with llama_index BaseEmbedding to
    work with this lib components. See BaseEmbedding class

    Attribute:
        model: SentenceTransformer object with BaseEmbedding interface
        precision: data type of output, for vector quantization
        convert_to_numpy: Whether convert embeddings to np array or not.

    Methods:
        Well, the function names are self-explained. :)
    
    *Note: This class return numpy ndarray or torch tensor, config with _convert_to_numpy
    """
    _embed_model:SentenceTransformer = PrivateAttr()
    _precision: str = PrivateAttr()
    _convert_to_numpy: bool = PrivateAttr()
    def __init__(self,model_path:str='../models/nomic-text-embed-v1.5',**kwargs:Any):
        super().__init__(**kwargs)
        self._embed_model =  SentenceTransformer(
            model_name_or_path=model_path,
            trust_remote_code=True,
            local_files_only=True
        )
        self._precision = 'float32'
        self._convert_to_numpy = True

    def _get_text_embedding(self, text:str):
        embeddings = self._embed_model.encode(
            sentences=text, 
            prompt='search_document',
            precision=self._precision,
            convert_to_numpy=self._convert_to_numpy
        )
        return embeddings

    async def _aget_text_embedding(self, text:str):
        embeddings = await self._embed_model.encode(
            sentences=text, 
            prompt='search_document',
            precision=self._precision,
            convert_to_numpy=self._convert_to_numpy
        )
        return embeddings
    
    def _get_query_embedding(self, query: str):
        embeddings = self._embed_model.encode(
            sentences=query, 
            prompt="search_query",
            precision=self._precision,
            convert_to_numpy=self._convert_to_numpy
        )
        return embeddings
    
    async def _aget_query_embedding(self, query: str):
        embeddings = await self._embed_model.encode(
            sentences=query, 
            prompt="search_query",
            precision=self._precision,
            convert_to_numpy=self._convert_to_numpy
        )
        return embeddings
    
    
class NomicEmbedQuantized(BaseEmbedding):
    _embed_model:Embed4All = PrivateAttr()
    def __init__(self,model_path:str='../models/',**kwargs:Any):
        super().__init__(**kwargs)
        self._embed_model =  Embed4All(
            model_path=model_path,
            allow_download=False,
            model_name='nomic-embed-text-v1.5.Q8_0.gguf'
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