import sys
import os
from dotenv import load_dotenv
import json
SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)
load_dotenv(dotenv_path=f"{SYSTEM_PATH}/backend/.env")
from backend.utils import *
from backend import NomicEmbedVision, NomicEmbed

"""
Script to index data
Input: directory of json not yet have embedding
Output: another directory of json have embedding
"""

directory_path = './resources/db'
save_directory_path = './resources/quantized-db'

text_embed_model = NomicEmbed()
vision_embed_model = NomicEmbedVision()
for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    json_id = data['id']

                    if 'content' in data: # embed paragraphs
                        for key, value in data['content'].items():
                            print(value['content'])
                            embedding = text_embed_model._get_text_embedding(value['content'])
                            embedding = binary_quantized(embedding)
                            base64_str = binary_array_to_base64(embedding)
                            value['embedding'] = base64_str

                    if 'images' in data: # embed images
                        for key, value in data['images'].items():
                            print(value['image_url'])
                            image_embedding = vision_embed_model.embed_image(value['image_url'])
                            base64_str = float32_vector_to_base64(image_embedding)
                            value['embedding'] = base64_str

                    if 'metadata' in data: # embed semantic metadata
                        semantic_metadata_dict = data['metadata'][json_id]
                        semantic_metadata_dict.pop('embedding', None)
                        semantic_metadata_str = "\n".join(f"{key}: {value}" for key, value in semantic_metadata_dict.items())
                        print(semantic_metadata_str)
                        embedding = text_embed_model._get_text_embedding(semantic_metadata_str)
                        embedding = binary_quantized(embedding)
                        base64_str = binary_array_to_base64(embedding)
                        semantic_metadata_dict['embedding'] = base64_str

                save_file_path = os.path.join(save_directory_path, filename)
                with open(save_file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=True, indent=4)
                print(f"Saved modified file: {filename}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in file {filename}: {e}")
            except Exception as e:
                print(f"Error reading file {filename}: {e}")