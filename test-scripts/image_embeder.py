import sys
import os
from dotenv import load_dotenv

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)
load_dotenv(dotenv_path=f"{SYSTEM_PATH}/backend/.env")

from backend import NomicEmbededVison, NomicEmbed
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer


url = "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png"
alt = "Google Logo"

nomic_embeded_vision = NomicEmbededVison()
img_embeddings = nomic_embeded_vision.embed_image(url)

nomic_embed = NomicEmbed()
alt_embeddings = nomic_embed._get_text_embedding(alt)
# Compare in distance and cosine similarity
distance = np.linalg.norm(img_embeddings - alt_embeddings)
print(f"Distance: {distance}")
similarity = cosine_similarity([img_embeddings], [alt_embeddings])
print(f"Cosine Similarity: {similarity}")