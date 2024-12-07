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
from qdrant_client.http.models.models import PointStruct, VectorParams

texts = [
    'Trump was shot and wounded in his upper right ear by Thomas Matthew Crooks, a 20-year-old man from Bethel Park, Pennsylvania, who fired eight rounds from an AR-15–style rifle from the roof of a nearby building. Crooks also killed one audience member and critically injured two others.',
    'The Fed lowered the federal funds target range by 25 basis points to 4.5%-4.75% at its November 2024 meeting, following a jumbo 50 basis point cut in September, in line with expectations.',
    'Here we are, Riding the sky, Painting the night with sun, You and I, mirrors of light, Twin flames of fire, Lit in another time and place',
    "Artificial intelligence is transforming industries worldwide.",
    "Learning new things every day keeps the mind sharp.",
    "The sun sets behind the mountains, casting a warm glow.",
    "In space, no one can hear you scream.",
    "Technology is rapidly evolving, bringing new possibilities.",
    "Reading books broadens your perspective and expands your knowledge.",
    "A journey of a thousand miles begins with a single step.",
    "The beauty of nature is something to be cherished every day.",
]


# Create embed model
embed_model_path = './resources/models/nomic-text-embed-v1.5'
embed_model = NomicEmbedQuantized()

embeddings = []
for text in texts:
    embedding = embed_model.get_text_embedding(text)
    boolean_array = np.array(embedding) > 0
    embeddings.append(boolean_array)

from backend.binary_quantized_rag import Retriever

retriever = Retriever()
points_structs = []
for i in range(len(texts)):
    payload = {}
    payload['text'] = texts[i]
    point_struct = PointStruct(
        id =i,
        vector=embeddings[i],
        payload=payload
    )
    points_structs.append(point_struct)

retriever.insert_points(points_structs)

while(1):
    query_embedding = embed_model.get_query_embedding(input("User query: "))
    query_embedding = np.array(query_embedding) > 0
    query_embedding = query_embedding.astype(int)

    results = retriever.search(query_vector=query_embedding)
    pprint(results)

