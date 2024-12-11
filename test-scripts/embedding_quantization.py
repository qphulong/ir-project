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
from backend import NomicEmbed, NomicEmbedQuantized, NomicEmbedVision
import qdrant_client
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.schema import TextNode
from qdrant_client.http.models.models import PointStruct, VectorParams, PointVectors
from memory_profiler import profile
from backend.binary_quantized_rag.retriever import Retriever
from backend.utils import binary_array_to_base64
from qdrant_client.local.qdrant_local import QdrantLocal
import sys
from backend.utils import *

import torch
import requests
from PIL import Image
from transformers import AutoTokenizer, AutoModel, AutoImageProcessor
import torch.nn.functional as F
import numpy as np

"""
Script to test retriever of quantized rag
_search_text_space
_search_metadata_space
_search_image_space (quantization not available)
"""

text_embed_model = NomicEmbed()
retriever = Retriever('./resources/quantized-db')

while(1):
    query = input("Query: ")
    query_embedding = text_embed_model._get_text_embedding(query)
    query_embedding = binary_quantized(query_embedding)
    pprint(
        retriever._search_metadata_space(query_embedding)
    )