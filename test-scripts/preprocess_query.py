import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend.query_preprocessor import QueryPreprocessor

"""
This script test functionality of QueryPreprocessor.

Usage: (on console interface)
User enter query and k suggestion, it should return a list of k refined query strings.
"""

query = ""

while query != "-q":
    query = input("Enter query: ")
    if query == "-q":
        break
    k = int(input("Enter k: "))
    preprocessor = QueryPreprocessor()
    processed_query = preprocessor.preprocess_query(query, k)
    if processed_query is None:
        print("An error occurred while processing the query.")
        continue
    print(f"Processed query: {processed_query}")
print("Exiting...")