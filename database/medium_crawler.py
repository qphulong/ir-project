import os
import json
import sys
import re
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=f"{SYSTEM_PATH}/backend/.env")
sys.path.append(SYSTEM_PATH)
from backend.utils import *
from backend import NomicEmbedVision, NomicEmbed

class MediumScraper:
    """
    A class to scrape Medium articles using the RapidAPI platform.

    Attributes:
        api_key (str): The API key for accessing RapidAPI.
        base_url (str): The base URL for the Medium-related API.
        text_embed_model (NomicEmbed): The model for text embedding.
        vision_embed_model (NomicEmbedVision): The model for image embedding.

    Methods:
        scrape_and_save_articles(keyword: str, k: int = 10):
            Scrapes and saves the top k articles from Medium based on the given keyword.

        get_embed_text(text: str) -> str:
            Generates and returns the base64-encoded text embedding for the given text.

        get_embed_img(img_url: str) -> str:
            Generates and returns the base64-encoded image embedding for the given image URL.

        search_posts(query: str, k: int = 10) -> List[str]:
            Searches Medium for the top k articles based on a query and returns a list of article IDs.

        fetch_article_details(article_id: str) -> Dict[str, str]:
            Fetches detailed information for a given article using its ID, including metadata, content, and images.

        fetch_article_html(article_id: str, fullpage: bool = True):
            Fetches the HTML content of an article by its ID. Optionally, you can fetch the full page.

        fetch_article_paragraphs(html: str, ID) -> Dict[str, Any]:
            Extracts and processes paragraphs from the HTML of an article, returning them with embeddings.

        fetch_article_images(html: str, ID) -> Dict:
            Extracts and processes images from the HTML of an article, returning the image URLs and embeddings.

        save_article_to_file(article_details: Dict[str, Any], article_id: str):
            Saves the article's details (including content and metadata) to a JSON file in the 'database/Medium' folder.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://medium2.p.rapidapi.com"
        self.text_embed_model = NomicEmbed()
        self.vision_embed_model = NomicEmbedVision()

        if not os.path.exists("database/Medium"):
            os.makedirs("database/Medium")

    def scrape_and_save_articles(self, keyword: str, k: int = 10):
        try:
            article_ids = self.search_posts(query=keyword, k=k)

            for i, article_id in enumerate(article_ids, start=1):
                print(f"Processing article {i}/{k} (ID: {article_id})")
                article_details = self.fetch_article_details(article_id)
                self.save_article_to_file(article_details, "medium_" + article_id)

        except Exception as e:
            print(f"Error during scraping and saving articles: {e}")

    def get_embed_text(self, text: str) ->str:
        embedding = self.text_embed_model.get_text_embedding(text)
        embedding = binary_quantized(embedding)
        return binary_array_to_base64(embedding)
    
    def get_embed_img(self, img_url:str)->str:
        img_embedding = self.vision_embed_model.embed_image(img_url)
        return float32_vector_to_base64(img_embedding)

    def search_posts(self, query: str, k: int = 10) -> List[str]:
        endpoint = f"{self.base_url}/search/articles"
        headers = {
            "x-rapidapi-host": "medium2.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }
        params = {"query": query}

        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            try:
                data = response.json()
                return data["articles"][:k]
            except Exception as e:
                print(f"Error parsing search response: {e}")
                print("Raw response content:", response.text)
                raise
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def fetch_article_details(self, article_id: str) -> Dict[str, str]:
        endpoint = f"{self.base_url}/article/{article_id}"
        headers = {
            "x-rapidapi-host": "medium2.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }

        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):  # Ensure the data is a dictionary
                    id = "medium_" + article_id
                    title = data.get("title", "No Title Available")
                    author = data.get("author", "Unknown Author")
                    published_date = data.get("published_at", "Unknown Date")
                    published_date = datetime.strptime(published_date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                    last_modified_date  = data.get("last_modified_at", "Unknown Date")
                    last_modified_date = datetime.strptime(last_modified_date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                    url = data.get("url", "No URL Available")

                    metadata : Dict[str, Any] = {
                        "url": url,
                        "pageId": article_id,
                        "author": author,
                        id: {
                            "title": title,
                            "published_date": published_date,
                            "last_update_date": last_modified_date,
                        }
                    }

                    embedding =""
                    for key, value in metadata[id].items():
                        embedding += f"{key}: {value}\n"
            
                    metadata[id]["embedding"] = self.get_embed_text(embedding)

                    soup = self.fetch_article_html(article_id)

                    post_data : Dict[str, Any] = {
                        "id": id,
                        "metadata": metadata,
                        "content": self.fetch_article_paragraphs(soup, id),
                        "images": self.fetch_article_images(soup, id)
                    }

                    return post_data
                else:
                    raise ValueError("Response data is not a dictionary.")
            except Exception as e:
                print(f"Error parsing article details: {e}")
                print("Raw response content:", response.text)
                raise
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        
    def fetch_article_html(self, article_id: str, fullpage: bool = True):
        endpoint = f"{self.base_url}/article/{article_id}/html"
        params = {"fullpage": str(fullpage).lower()}

        try:
            headers = {
                "x-rapidapi-host": "medium2.p.rapidapi.com",
                "x-rapidapi-key": self.api_key
            }
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status() 

            json_data = response.json()

            return json_data["html"]
            

        except requests.exceptions.RequestException as req_err:
            print(f"Request error while fetching HTML for article {article_id}: {req_err}")
            raise
        except Exception as e:
            print(f"Unexpected error while fetching HTML for article {article_id}: {e}")
            raise

        
    def fetch_article_paragraphs(self, html: str, ID) -> Dict[str, Any]:
        cleaned_html = html

        soup = BeautifulSoup(cleaned_html, 'html.parser')

        paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]

        result: Dict[str, Any] = {}

        for i, text in enumerate(paragraphs, start=1):
            if text:
                text_cleaned = re.sub(r'"', '', text)
                key = f"{ID}_text_{i}"
                result[key] = {"content": text_cleaned, "embedding": self.get_embed_text(text_cleaned)}

        return result
    
    def fetch_article_images(self, html:str, ID) -> Dict:
        images: Dict[str, Any] = {}

        soup = BeautifulSoup(html, 'html.parser')

        for i, img in enumerate(soup.find_all('img'), start=1):
            img_url = img.get('src')
            if img_url:
                try:
                    img_url = json.loads(f'"{img_url}"') if '\\' in img_url else img_url
                except json.JSONDecodeError:
                    pass
            images_info: Dict[str, Any] = {
                "image_url": img_url.strip('"'),
                "embedding": self.get_embed_img(img_url)
            }

            key = f"{ID}_image_{i}"
            images[key] = images_info

        return images

    def save_article_to_file(self, article_details: Dict[str, Any], article_id: str):
        file_name = f"database/Medium/{article_id}.json"  

        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(article_details, file, ensure_ascii=True, indent=4)


if __name__ == "__main__":
    API_KEY = "a1256ae1c0mshc4ff25bf27c7166p1c624cjsn0d32e0d704d1"
    scraper = MediumScraper(api_key=API_KEY)

    query = input("Enter search query (keyword): ")
    top_k = int(input("Enter the number of top articles to fetch: "))

    try:
        article_ids = scraper.search_posts(query=query, k=top_k)

        for i, article_id in enumerate(article_ids, start=1):
            article_details = scraper.fetch_article_details(article_id)
            scraper.save_article_to_file(article_details, "medium_" + article_id)

    except Exception as e:
        print("Error:", e)
