import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend import env
import numpy as np
from pprint import pprint
from qdrant_client import QdrantClient, models
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.vector_stores import VectorStoreQuery, VectorStoreQueryResult
from llama_index.core import VectorStoreIndex
from backend import NomicEmbed, NomicEmbedQuantized
import qdrant_client
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.schema import TextNode
from qdrant_client.http.models.models import PointStruct, VectorParams, PointVectors
from memory_profiler import profile
from backend.binary_quantized_rag.retriever import Retriever
from backend.utils import binary_array_to_base64

import sys

retriever = Retriever(database_path='./resources/quantized-db')
embed_model = NomicEmbedQuantized()

while(1):
    query_embedding = embed_model.get_query_embedding(input("User query: "))
    # query_embedding = np.array(query_embedding) > 0
    # query_embedding = query_embedding.astype(np.uint8)
    pprint(retriever._search_image_space(
        query_vector=query_embedding
        )
    )


