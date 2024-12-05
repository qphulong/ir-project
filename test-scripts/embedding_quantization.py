import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from dotenv import load_dotenv

load_dotenv('.env')
import numpy as np
from pprint import pprint
from qdrant_client import QdrantClient, models
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.vector_stores import VectorStoreQuery, VectorStoreQueryResult
from llama_index.core import VectorStoreIndex
from backend import NomicEmbed
import qdrant_client
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.schema import TextNode

# Step 1: Initialize Qdrant client with in-memory storage
client = qdrant_client.QdrantClient(location=":memory:")
collection_name = "my-test-db"

quantization_config=models.BinaryQuantization(
    binary=models.BinaryQuantizationConfig(
        always_ram=True  # Keep binary embeddings in RAM for fast access
    )
)

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=768,  # Adjust this to your embedding size
            distance=models.Distance.MANHATTAN,
            quantization_config=quantization_config,
        ),
        quantization_config=quantization_config
    )
# Step 2: Create Qdrant Vector Store
vector_store = QdrantVectorStore(client=client, collection_name="my-test-db")

# Create sample TextNodes
text_node_0 = TextNode(text = 'Trump was shot and wounded in his upper right ear by Thomas Matthew Crooks, a 20-year-old man from Bethel Park, Pennsylvania, who fired eight rounds from an AR-15–style rifle from the roof of a nearby building. Crooks also killed one audience member and critically injured two others.')
text_node_1 = TextNode(text = 'The Fed lowered the federal funds target range by 25 basis points to 4.5%-4.75% at its November 2024 meeting, following a jumbo 50 basis point cut in September, in line with expectations.')
text_node_2 = TextNode(text = 'Here we are, Riding the sky, Painting the night with sun, You and I, mirrors of light, Twin flames of fire, Lit in another time and place')
nodes_list = [text_node_0,text_node_1,text_node_2]

# Create embed model
embed_model_path = '../models/nomic-text-embed-v1.5'
embed_model = NomicEmbed(model_path=embed_model_path)

for node in nodes_list:
    embedding = embed_model.get_text_embedding(node.text)
    boolean_array = np.array(embedding) > 0
    node.embedding = boolean_array

vector_store.add(nodes=nodes_list)
my_collection = vector_store.client._client.collections['my-test-db']
my_collection.vectors[''] = my_collection.vectors[''].astype(bool)

query_embedding = embed_model.get_query_embedding("describe the poem")
query_embedding = np.array(query_embedding) > 0
query_embedding = query_embedding.astype(int)
vector_store_query = VectorStoreQuery(
    query_embedding=query_embedding, similarity_top_k=3, mode='default'
)
results = vector_store.query(vector_store_query)
pprint(results)

storage_context = StorageContext.from_defaults(
    vector_store=vector_store,
)

storage_context.persist('./asjdhkaj')

# # Step 3: Build VectorStoreIndex
# documents = [Document(text="The cat is eating"), Document(text="The dog is swimming")]
# storage_context = StorageContext.from_defaults(vector_store=vector_store)
# index = VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context)

# # Query the index
# query_engine = index.as_query_engine()

# response = query_engine.query("What is the feline doing")
# print(response)


