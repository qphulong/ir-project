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
from qdrant_client.conversions.common_types import ScoredPoint
from qdrant_client.http.models.models import PointStruct, VectorParams
from ..utils import *
import numpy as np

class Retriever():
    """
    Retriever class. This class assume the path to database of json exist.

    Attributes:
        database_path (str): Path to resource (database + index)
    """
    def __init__(
        self,
        database_path:str='./resources/quantized-db',
        vector_size: int = 768,
    ):
        self.database_path = database_path
        self.vector_size = vector_size
        self.qdrant_local = QdrantLocal(location=":memory:")
        self.text_space = None
        self.metadata_space = None
        self.image_space = None
        self._setup()
        
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
                    if 'content' in data and data['content']:
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
                        
    def search_text_space(self, query_vector:np.ndarray,top_k:int = 8) -> Tuple[List[str],List[ScoredPoint]]:
        """
        Example usage:
        query = input('User: ')
        query_embedding = embed_model._get_text_embedding(query)
        query_embedding = binary_quantized(query_embedding)
        search_text_space(query_embedding)
        """
        results = self.qdrant_local.search(
            collection_name='text_space',
            query_vector=query_vector,
            limit=top_k,
        )
        return self._get_texts_base_on_search_results(results),results
    
    def _get_texts_base_on_search_results(self, results:List[ScoredPoint])->List[str]:
        texts = []
        for result in results:
            id = result.id
            post_id = id.split('_text_')[0]
            json_file_path = os.path.join(self.database_path, f"{post_id}.json")

            # Check if the file exists
            if os.path.exists(json_file_path):
                # Open the JSON file and load its data
                with open(json_file_path, 'r') as file:
                    data = json.load(file)

                # Retrieve the image URL from the JSON structure
                text = data['content'][result.id]['content']
                texts.append(text)
        return texts

    
    def _setup_image_space(self):
        """Prepare the image_space collection"""
        # TODO this code can be optimized
        self.qdrant_local.create_collection(
            collection_name='image_space',
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=models.Distance.COSINE,
            ),
        )
        self.image_space = self.qdrant_local.collections['image_space']
        
        n_embeddings = 0
        for filename in os.listdir(self.database_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.database_path, filename)
                
                # Read the JSON file
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    # Check if 'content' key exists in the file
                    if 'images' in data and data['images']:
                        # For each entry in the 'content', extract the embedding
                        for key, value in data['images'].items():
                            embedding = base64_to_float32_vector(value.get('embedding'))
                            self.image_space._add_point(
                                point=PointStruct(
                                    id = key,
                                    vector=embedding,
                                    payload=None
                                )
                            )
                            n_embeddings+=1
        # shorten and change dtype of vectors
        self.image_space.vectors[''] = self.image_space.vectors[''].astype(np.float32)[:n_embeddings]

    def search_image_space(self, query_vector:np.ndarray,top_k:int = 8) -> Tuple[List[str],List[ScoredPoint]]:
        """
        Example usage:
        query = input("Query: ")
        query_embedding = text_embed_model._get_embeddings_for_image_query(query)
        search_image_space(query_embedding)
        """
        results =  self.qdrant_local.search(
            collection_name='image_space',
            query_vector=query_vector,
            limit=top_k,
        )
        return self._get_images_based_on_search_results(results),results
    
    def _setup_metadata_space(self):
        """Prepare the metadata_space collection"""
        # TODO this code can be optimized
        self.qdrant_local.create_collection(
            collection_name='metadata_space',
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
        self.metadata_space = self.qdrant_local.collections['metadata_space']
        
        n_embeddings = 0
        for filename in os.listdir(self.database_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.database_path, filename)
                
                # Read the JSON file
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    # Check if 'content' key exists in the file
                    if 'id' in data:
                        # For each entry in the 'content', extract the embedding
                        dynamic_id = data['id']
                        if dynamic_id not in data['metadata']:
                            continue
                        embedding = base64_to_binary_array(data['metadata'][dynamic_id]['embedding'])
                        self.metadata_space._add_point(
                            point=PointStruct(
                                id = dynamic_id,
                                vector=embedding,
                                payload=None
                            )
                        )
                        n_embeddings+=1
        # shorten and change dtype of vectors
        self.metadata_space.vectors[''] = self.metadata_space.vectors[''].astype(np.uint8)[:n_embeddings]

    def search_metadata_space(self, query_vector:np.ndarray,top_k:int = 8)->Tuple[List[str],List[ScoredPoint]]:
        """Same for search_text_space"""
        results =  self.qdrant_local.search(
            collection_name='metadata_space',
            query_vector=query_vector,
            limit=top_k,
        )
        return self._get_metadatas_base_on_search_results(results),results
    
    def _get_metadatas_base_on_search_results(self,results:List[ScoredPoint])->List[str]:
        metadatas = []
        for result in results:
            post_id = result.id
            json_file_path = os.path.join(self.database_path, f"{post_id}.json")

            # Check if the file exists
            if os.path.exists(json_file_path):
                # Open the JSON file and load its data
                with open(json_file_path, 'r') as file:
                    data = json.load(file)

                # Retrieve the image URL from the JSON structure
                metadata = data['metadata'][post_id]
                metadata_str = "\n".join(f"{key}: {value}" for key, value in metadata.items() if key != 'embedding')
                metadatas.append(metadata_str)
        return metadatas

    def _setup(self):
        self._setup_text_space()
        self._setup_image_space()
        self._setup_metadata_space()

    def _get_images_based_on_search_results(self, results:List[ScoredPoint]) -> List[str]:
        img_urls = []
        for result in results:
            id = result.id
            post_id = id.split('_image_')[0]
            json_file_path = os.path.join(self.database_path, f"{post_id}.json")

            # Check if the file exists
            if os.path.exists(json_file_path):
                # Open the JSON file and load its data
                with open(json_file_path, 'r') as file:
                    data = json.load(file)

                # Retrieve the image URL from the JSON structure
                img_url = data['images'][result.id]['image_url']
                img_urls.append(img_url)
        return img_urls
    
    def add_point_to_text_space(self, point_id:str, vector: np.ndarray):
        """
        Adds a point with the specified ID and vector to the text space.
        Args:
            point_id (str): A unique identifier for the point to be added.
            vector (np.ndarray): The vector representation of the point. MUST be binary quantized. (int8)

        Returns:
            None
        """
        number_of_vectors = len(self.text_space.vectors[''])
        self.text_space._add_point(
            point=PointStruct(
                id = point_id,
                vector=vector,
                payload=None
            )
        )
        self.text_space.vectors[''] = self.text_space.vectors[''][:number_of_vectors+1]

    def add_point_to_metadata_space(self, point_id:str, vector: np.ndarray):
        """Same for above"""
        number_of_vectors = len(self.metadata_space.vectors[''])
        self.metadata_space._add_point(
            point=PointStruct(
                id = point_id,
                vector=vector,
                payload=None
            )
        )
        self.metadata_space.vectors[''] = self.metadata_space.vectors[''][:number_of_vectors+1]

    def add_point_to_image_space(self, point_id:str, vector: np.ndarray):
        """
        Adds a point with the specified ID and vector to the image space.

        Args:
            point_id (str): A unique identifier for the point to be added.
            vector (np.ndarray): The vector representation of the point. Must be float32

        Returns:
            None
        """
        number_of_vectors = len(self.image_space.vectors[''])
        self.image_space._add_point(
            point=PointStruct(
                id = point_id,
                vector=vector,
                payload=None
            )
        )
        self.image_space.vectors[''] = self.image_space.vectors[''][:number_of_vectors+1]