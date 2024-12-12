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

# Test 1
text_embed_model = NomicEmbed()
retriever = Retriever('./resources/CNN')

while(1):
    query = input("Query: ")
    query_embedding = text_embed_model._get_embeddings_for_image_query(query)
    # query_embedding = binary_quantized(query_embedding)
    pprint(
        retriever._search_image_space(query_embedding)
    )
# while(1):
#     query = input("Query: ")
#     query_embedding = text_embed_model._get_text_embedding(query)
#     query_embedding = binary_quantized(query_embedding)
#     pprint(
#         retriever._search_text_space(query_embedding)
#     )


# # Test2
# text_list = [
#     "The Enigma has an electromechanical rotor mechanism that scrambles the 26 letters of the alphabet. In typical use, one person enters text on the Enigma's keyboard and another person writes down which of the 26 lights above the keyboard illuminated at each key press. If plaintext is entered, the illuminated letters are the ciphertext. Entering ciphertext transforms it back into readable plaintext. The rotor mechanism changes the electrical connections between the keys and the lights with each keypress.",
#     "Europa has the smoothest surface of any known solid object in the Solar System. The apparent youth and smoothness of the surface is due to a water ocean beneath the surface, which could conceivably harbor extraterrestrial life, although such life would most likely be that of single celled organisms and bacteria-like creatures.[18] The predominant model suggests that heat from tidal flexing causes the ocean to remain liquid and drives ice movement similar to plate tectonics, absorbing chemicals from the surface into the ocean below",
#     "The capture of Leningrad was one of three strategic goals of the German Operation Barbarossa and as a result, Leningrad was the main target of Army Group North. The strategy was motivated by Leningrad's political status as the former capital of Russia as well as by Leningrad's political status as the symbolic capital of the Russian Revolution and its symbolic status as the ideological center of Bolshevism, hated by the Nazi Party, the city's military importance as a main base of the Soviet Baltic Fleet, and its industrial strength, including its numerous arms factories.[18] In 1939, the city was responsible for 11% of all Soviet industrial output.",
#     "The United States created the Tenth Army, a cross-branch force consisting of the U.S. Army 7th, 27th, 77th and 96th Infantry Divisions with the 1st, 2nd, and 6th Marine Divisions, to seize the island. The Tenth Army was unique in that it had its own Tactical Air Force (joint Army-Marine command) and was supported by combined naval and amphibious forces. Opposing the Allied forces on the ground was the Japanese Lieutenant General Mitsuru Ushijima's Thirty-Second Army, a mixed force consisting of regular army troops, naval infantry and conscripted local Okinawans. Total Japanese troop strength on the island was about 100,000 at the onset of the invasion. The Battle of Okinawa was the single longest sustained carrier campaign of the Second World War",
#     "Some researchers are going to put you to sleep. During the two days that your sleep will last, they will briefly wake you up either once or twice, depending on the toss of a fair coin (Heads: once; Tails: twice). After each waking, they will put you back to sleep with a drug that makes you forget that waking. When you are first awakened, to what degree ought you believe that the outcome of the coin toss is Heads?",
#     "Erika is a German marching song. It is primarily associated with the German Army, especially that of Nazi Germany, although its text has no political content.[1] It was created by Herms Niel and published in 1938, and soon came into usage by the Wehrmacht. It was frequently played during Nazi Party public events.[citation needed] According to British soldier, historian, and author Major General Michael Tillotson, it was the single most popular marching song of any country during the Second World War",
#     "In 1896, Alexander Tille made the first English translation of Thus Spoke Zarathustra, rendering Übermensch as Beyond-Man. In 1909, Thomas Common translated it as Superman, following the terminology of George Bernard Shaw's 1903 stage play Man and Superman. Walter Kaufmann lambasted this translation in the 1950s for two reasons: first, the failure of the English prefix super to capture the nuance of the German über (though in Latin, its meaning of above or beyond is closer to the German); and second, for promoting misidentification of Nietzsche's concept with the comic-book character Superman. Kaufmann and others preferred to translate Übermensch as overman. A translation like superior humans might better fit the concept of Nietzsche as he unfolds his narrative. Scholars continue to employ both terms, some simply opting to reproduce the German word",
#     "The cat (Felis catus), also referred to as the domestic cat or house cat, is a small domesticated carnivorous mammal. It is the only domesticated species of the family Felidae. Advances in archaeology and genetics have shown that the domestication of the cat occurred in the Near East around 7500 BC. It is commonly kept as a pet and farm cat, but also ranges freely as a feral cat avoiding human contact.",
#     "Author: Thomas Bergesen",
#     "Singer: Merethe Soltvedt",#10
#     "Song: We Are Legends",
#     "Author: Thomas Harris",#
# ]

# embed_model = NomicEmbed()
# qdrant_local = QdrantLocal(location=":memory:")
# qdrant_local.create_collection(
#     collection_name='text_space',
#     vectors_config=VectorParams(
#         size=768,
#         distance=models.Distance.MANHATTAN,
#         quantization_config= models.BinaryQuantization(
#             binary=models.BinaryQuantizationConfig(
#                 always_ram=True
#             )
#         )
#     )  
# )
# text_space = qdrant_local.collections['text_space']
# for i,text in enumerate(text_list):
#     embedding = embed_model._get_text_embedding(text)
#     embedding = binary_quantized(embedding)
#     text_space._add_point(
#         point=PointStruct(
#             id = i+1,
#             vector=embedding,
#             payload=None
#         )
#     )
# text_space.vectors[''] = text_space.vectors[''].astype(np.uint8)[:len(text_list)]

# while(1):
#     query = input('User: ')
#     query_embedding = embed_model._get_text_embedding(query)
#     query_embedding = binary_quantized(query_embedding)
#     pprint(
#         qdrant_local.search(
#             collection_name='text_space',
#             query_vector=query_embedding,
#             limit=8,
#         )
#     )
