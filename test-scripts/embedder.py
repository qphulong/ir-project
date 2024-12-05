import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend import NomicEmbed

"""
This script test functionality of NomicEmbed class
"""

model_path = '../models/nomic-text-embed-v1.5'
model = NomicEmbed(model_path=model_path)

texts =[
    "I like cat",
]

embedings = model._get_text_embeddings(texts=texts)

print(embedings[0].shape)
print(embedings[0][0].__class__)
print(embedings[0][0:10])