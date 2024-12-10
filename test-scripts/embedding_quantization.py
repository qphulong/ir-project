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

import sys

# texts = [
#     'Trump was shot and wounded in his upper right ear by Thomas Matthew Crooks, a 20-year-old man from Bethel Park, Pennsylvania, who fired eight rounds from an AR-15–style rifle from the roof of a nearby building. Crooks also killed one audience member and critically injured two others.',
#     'The Fed lowered the federal funds target range by 25 basis points to 4.5%-4.75% at its November 2024 meeting, following a jumbo 50 basis point cut in September, in line with expectations.',
#     'Here we are, Riding the sky, Painting the night with sun, You and I, mirrors of light, Twin flames of fire, Lit in another time and place',
#     "Artificial intelligence is transforming industries worldwide.",
#     "Learning new things every day keeps the mind sharp.",
#     "The sun sets behind the mountains, casting a warm glow.",
#     "In space, no one can hear you scream.",
#     "Technology is rapidly evolving, bringing new possibilities.",
#     "Reading books broadens your perspective and expands your knowledge.",
#     "A journey of a thousand miles begins with a single step.",
#     "The beauty of nature is something to be cherished every day.",
#     "Author: Stephen King",
#     "Author: Jessica Jone",
#     "Publish date: 10 Jan 2022",
#     "Publish date: 15 Aug 2022",
#     "Publish date: 20 Jan 2022",
#     "The sun set behind the mountains, casting a golden glow over the valley.",
#     "She opened the book and began reading the first chapter with great interest.",
#     "The dog ran across the park, chasing after a frisbee.",
#     "A gentle breeze whispered through the trees as the leaves danced in the wind.",
#     "He couldn't believe his eyes when he saw the shooting star streak across the sky.",
#     "The city streets were bustling with life, filled with people and the sounds of traffic.",
#     "The aroma of freshly brewed coffee filled the room, waking her up instantly.",
#     "As the rain poured down, they sought shelter under the old oak tree.",
#     "She smiled as she watched the children play in the park, their laughter echoing in the air.",
#     "The detective studied the clues carefully, trying to piece together the mystery.",
#     "The waves crashed against the shore, their rhythmic sound soothing to the ear.",
#     "He carefully painted the canvas, adding details with each stroke of the brush.",
#     "The clock struck midnight, signaling the start of a new adventure.",
#     "The forest was quiet, except for the occasional rustle of leaves in the wind.",
#     "They sat around the campfire, sharing stories and roasting marshmallows.",
#     "Her heart raced as she stood on the edge of the cliff, gazing at the vast ocean below.",
#     "The small village was tucked away in the hills, untouched by time.",
#     "He had always dreamed of traveling the world and experiencing new cultures.",
#     "The stars twinkled brightly in the clear night sky, a mesmerizing sight.",
#     "She found a secret passage hidden behind a bookshelf in the old library.",
#     "The mountain air was crisp and fresh, invigorating every breath she took.",
#     "The puppy wagged its tail excitedly as it played with a ball in the yard.",
#     "A soft melody played in the background as they danced under the moonlight.",
#     "The train chugged along the tracks, taking passengers on a scenic journey.",
#     "He opened the envelope and found a letter that would change his life forever.",
#     "The garden was alive with color, with flowers in full bloom everywhere.",
#     "The chef added a pinch of salt to the dish, bringing all the flavors together.",
#     "They walked hand in hand through the park, enjoying the beauty of the afternoon.",
#     "The old house creaked and groaned as the wind blew through the cracks.",
#     "She couldn’t wait to see the look on his face when she gave him the surprise gift.",
#     "The mountain trail was steep, but the view from the top was worth the effort."
# ]

# embed_model_path = './resources/models/nomic-text-embed-v1.5'
# embed_model = NomicEmbedQuantized()

# embeddings = []
# for text in texts:
#     embedding = embed_model.get_text_embedding(text)
#     boolean_array = np.array(embedding) > 0
#     embeddings.append(boolean_array)

# from backend.binary_quantized_rag import Retriever

# retriever = Retriever()
# points_structs = []
# for i in range(len(texts)):
#     payload = {}
#     payload['text'] = texts[i]
#     point_struct = PointStruct(
#         id =i,
#         vector=embeddings[i],
#         payload=None
#     )
#     points_structs.append(point_struct)
# retriever.insert_points(points_structs)


# retriever.qdrant_local.collections['default'].vectors[''] = retriever.qdrant_local.collections['default'].vectors[''].astype(bool)[:len(texts)]

# for i in range(3):
#     query_embedding = embed_model.get_query_embedding(input("User query: "))
#     query_embedding = np.array(query_embedding) > 0
#     query_embedding = query_embedding.astype(int)

#     results = retriever.search(query_vector=query_embedding)
#     pprint(results)

# embed_model = NomicEmbedQuantized()
# text = 'sometext'
# embedding = embed_model.get_text_embedding(text)
# boolean_array = np.array(embedding) > 0

retriever = Retriever(database_path='./resources/quantized-db-processed')
embed_model = NomicEmbedQuantized()

while(1):
    query_embedding = embed_model.get_query_embedding(input("User query: "))
    query_embedding = np.array(query_embedding) > 0
    query_embedding = query_embedding.astype(np.uint8)
    pprint(retriever._search_text_space(
        query_vector=query_embedding
        )
    )