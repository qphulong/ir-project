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
from ..utils import base64_to_binary_array
import numpy as np

class Retriever():
    """
    Retriever class. This class assume the path to database of json exist.

    Attributes:
        database_path (str): Path to resource (database + index)
    """
    def __init__(
        self,
        database_path:str='./resource/quantized-db',
        vector_size: int = 768,
    ):
        self.database_path = database_path
        self.vector_size = vector_size
        self.qdrant_local = QdrantLocal(location=":memory:")
        self.text_space = None
        self.metadata_space = None
        self.image_space = None
        self._setup_text_space()
        
    def _setup_text_space(self):
        """Prepare the text_space collection"""
        # TODO this code can be optimized
        self.qdrant_local.create_collection(
            collection_name='text_space',
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=models.Distance.MANHATTAN,
                quantization_config= models.BinaryQuantization(
                    binary=models.BinaryQuantizationConfig(
                        always_ram=True
                    )
                ),
            ),
        )
        self.text_space = self.qdrant_local.collections['text_space']
        
        n_embeddings = 0
        for filename in os.listdir(self.database_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.database_path, filename)
                
                # Read the JSON file
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    # Check if 'content' key exists in the file
                    if 'content' in data:
                        # For each entry in the 'content', extract the embedding
                        for key, value in data['content'].items():
                            embedding = base64_to_binary_array(value.get('embedding'))
                            self.text_space._add_point(
                                point=PointStruct(
                                    id = key,
                                    vector=embedding,
                                    payload=None
                                )
                            )
                            n_embeddings+=1
        # shorten and change dtype of vectors
        self.text_space.vectors[''] = self.text_space.vectors[''].astype(np.uint8)[:n_embeddings]
                        
    def _search_text_space(self, query_vector:np.ndarray,top_k:int = 8):
        return self.qdrant_local.search(
            collection_name='text_space',
            query_vector=query_vector,
            limit=top_k,
        )

    def _setup(self):
        binary_quantization_config = models.BinaryQuantization(
            binary=models.BinaryQuantizationConfig(
                always_ram=True
            )
        )

        self.qdrant_local.create_collection(
            collection_name='text_space',
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=models.Distance.MANHATTAN,
                quantization_config=binary_quantization_config,
            ),
        )
        self.text_space = self.qdrant_local.collections['text_space']

        self.qdrant_local.create_collection(
            collection_name='metadata_space',
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=models.Distance.MANHATTAN,
                quantization_config=binary_quantization_config,
            ),
        )
        self.metadata_space = self.qdrant_local.collections['metadata_space']

        self.qdrant_local.create_collection(
            collection_name='image_space',
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=models.Distance.MANHATTAN,
                quantization_config=binary_quantization_config,
            ),
        )
        self.image_space = self.qdrant_local.collections['image_space']



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
    