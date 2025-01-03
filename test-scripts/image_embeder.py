import sys
import os
from dotenv import load_dotenv

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)
load_dotenv(dotenv_path=f"{SYSTEM_PATH}/backend/.env")

from backend import NomicEmbedVision, NomicEmbed
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer

"""This script test functionality of NomicEmbededVison module"""

url = "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png"
alt = "Google Logo"

nomic_embeded_vision = NomicEmbedVision()
img_embeddings = nomic_embeded_vision.embed_image(url)

nomic_embed = NomicEmbed()
alt_embeddings = nomic_embed._get_text_embedding(alt)
# Compare in distance and cosine similarity
distance = np.linalg.norm(img_embeddings - alt_embeddings)
print(f"Distance: {distance}")
similarity = cosine_similarity([img_embeddings], [alt_embeddings])
print(f"Cosine Similarity: {similarity}")


from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from openai import OpenAI

# Define the labels
labels = ['Vision', 'Text']

# Data
available_ids = [1, 19, 128, 171, 184, 300, 311]
N = len(available_ids)
urls: list[str] = []
for i in range(N):
    ID = available_ids[i]
    ID = str(ID).zfill(12)
    urls.append(f'http://images.cocodataset.org/test-stuff2017/{ID}.jpg')

# get alt text with OpenAI
client = OpenAI()
responses = []
for i in range(N):
    responses.append(client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe the image as clear as posible."},
            {
            "type": "image_url",
            "image_url": {
                "url": urls[i],
            },
            },
        ],
        }
    ],
    max_tokens=500,
    ))

print(responses)

alt_texts = [response.choices[0].message.content for response in responses]

# Get embeddings
img_embeddings = [nomic_embeded_vision.embed_image(url) for url in urls]
alt_embeddings = [nomic_embed._get_text_embedding(alt) for alt in alt_texts]
embeddings = img_embeddings + alt_embeddings

# create confusion matrix base on cosine similarity
cf = np.zeros((N*2, N*2))
for i in range(N*2):
    for j in range(N*2):
        x_embedding = embeddings[i]
        y_embedding = embeddings[j]
        similarity = cosine_similarity([x_embedding], [y_embedding])
        cf[i][j] = similarity

# Plot confusion matrix
fig, ax = plt.subplots()
cax = ax.matshow(cf, cmap='hot')
fig.colorbar(cax)
ax.set_xticklabels([''] + labels)
ax.set_yticklabels([''] + labels)
plt.show()