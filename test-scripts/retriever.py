import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend import Retriever
from llama_index.core.schema import Document as LLamaDocument

retriver = Retriever(
    resource_path='../test-big-database',
    embed_model_path='../models/',
)

while(1):
    user_query = input("User query: ")
    if user_query == '/exit':
        break
    results = retriver.retrieve(user_query)
    for id in results.ids:
        print(retriver.get_node_by_id(id).text,'\n')

retriver.persist_to_disk()

