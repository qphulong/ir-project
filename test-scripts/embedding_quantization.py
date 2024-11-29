import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend import Retriever

retriever = Retriever(resource_path='../test-big-database',embed_model_path='../models/')

print(len(retriever.vector_store_index.docstore.docs))