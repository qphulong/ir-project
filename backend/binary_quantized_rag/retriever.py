from ..nomic_embed import NomicEmbed, NomicEmbedQuantized
from typing import List,Tuple, Iterable
from llama_index.core.schema import Document as LLamaDocument
from llama_index.core.schema import TextNode
import json
import os
from ..semantice_chunker import SemanticChunker
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core import load_index_from_storage
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores import VectorStoreQuery, VectorStoreQueryResult
from qdrant_client.local.qdrant_local import QdrantLocal
from qdrant_client import QdrantClient, models
from qdrant_client.http.models.models import PointStruct, VectorParams

class Retriever():
    """
    Retriever class.

    Attributes:
        resource_path (str): Path to resource (database + index)
        embed_model_path (str): The path to the local embedding model.
        embed_model (NomicEmbedQuantized): The embedding model used for vectorizing the data.
    """
    def __init__(
        self,
        resource_path:str='',
        embed_model_path:str='',
        vector_size: int = 768,
    ):
        self.database_path = os.path.join(resource_path, 'database')
        self.index_path = os.path.join(resource_path, 'index')
        self.embed_model_path = embed_model_path
        self.embed_model = NomicEmbedQuantized()
        self.vector_size = vector_size
        self.qdrant_local = QdrantLocal(location=":memory:")
        self.collection_name = "default"
        self._setup()
        
    def _setup(self):
        binary_quantization_config = models.BinaryQuantization(
            binary=models.BinaryQuantizationConfig(
                always_ram=True
            )
        )

        self.qdrant_local.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=models.Distance.MANHATTAN,
                quantization_config=binary_quantization_config
            ),
        )

    def insert_points(self, points: Iterable[PointStruct]):
        self.qdrant_local.upload_points(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector,top_k:int = 8):
        return self.qdrant_local.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
        )