import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend.QueryPreprocessor import QueryPreprocessor

query = ""

while query != "-q":
    query = input("Enter query: ")
    if query == "-q":
        break
    preprocessor = QueryPreprocessor()
    processed_query = preprocessor.preprocess_query(query)
    print(f"Processed query: {processed_query}")
print("Exiting...")