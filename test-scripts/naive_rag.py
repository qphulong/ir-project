import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend import NaiveRAG
from llama_index.core.schema import Document as LLamaDocument

"""Script to test functionality of naive rag, to exit conversation type '/exit' """

naive_rag = NaiveRAG(
    resource_path='./resources/test-big-database',
    embed_model_path='./resources/models/',
)

naive_rag.begin()

