import os
import json
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime

class MediumScraper:
    """
    A class to scrape Medium articles using the RapidAPI platform.

    Attributes:
        api_key (str): The API key for accessing RapidAPI.
        base_url (str): The base URL for the Medium-related API.

    Methods:
        search_posts(query: str, k: int) -> List[str]:
            Searches Medium for the top k articles based on a query.
        
        fetch_article_details(article_id: str) -> Dict[str, str]:
            Fetches detailed information for a given article using its ID.
        
        save_article_to_file(article_details: Dict[str, str], article_id: str):
            Saves the article's details into a file in the Medium folder.
    """

    def __init__(self, api_key: str):
        """
        Initializes the MediumScraper with the RapidAPI key.

        Args:
            api_key (str): Your RapidAPI key for authentication.
        """
        self.api_key = api_key
        self.base_url = "https://medium2.p.rapidapi.com"

        if not os.path.exists("database/Medium"):
            os.makedirs("database/Medium")

    def search_posts(self, query: str, k: int = 10) -> List[str]:
        """
        Searches Medium for the top k articles based on a query.

        Args:
            query (str): The search query string.
            k (int): The number of top articles to fetch (default: 10).

        Returns:
            List[str]: A list of article IDs.
        """
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
        """
        Fetches detailed information for a given article using its ID.

        Args:
            article_id (str): The article ID to fetch details for.

        Returns:
            Dict[str, str]: A dictionary with article details like title, link, and content.
        """
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
        """
        Fetches the HTML content of an article using its ID.

        Args:
            article_id (str): The article ID to fetch HTML content for.
            fullpage (bool): Whether to fetch the full page content (default: True).

        Returns:
            str: The HTML content of the article.
        """
        endpoint = f"{self.base_url}/article/{article_id}/html"
        params = {"fullpage": str(fullpage).lower()}

        try:
            headers = {
                "x-rapidapi-host": "medium2.p.rapidapi.com",
                "x-rapidapi-key": self.api_key
            }
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status() 

            soup = BeautifulSoup(response.text, 'html.parser')

            return soup
            

        except requests.exceptions.RequestException as req_err:
            print(f"Request error while fetching HTML for article {article_id}: {req_err}")
            raise
        except Exception as e:
            print(f"Unexpected error while fetching HTML for article {article_id}: {e}")
            raise

        
    def fetch_article_paragraphs(self, soup, ID) -> Dict[str, Any]:
        paragraphs = [p.get_text(strip = True) for p in soup.find_all('p')]
        
        result : Dict[str, Any] = {}

        for i, text in enumerate(paragraphs, start=1):
            if text:
                paragraph: Dict[str, Any] = {
                        "content": text
                }
                key = f"{ID}_text_{i}"
                result[key] =  paragraph
                return result

        return paragraphs
    
    def fetch_article_images(self, soup, ID) -> Dict:
        images : Dict[str, Any] = {}
        for i, img in enumerate(soup.find_all('img'), start=1):
            img_url = img.get('src')
            img_tag = img.get('alt', '')

            images_info : Dict[str, Any] = {
                "image_url":img_url,
                "image_alt": img_tag
            }
            key = f"{ID}_image_{i}"
            images[key] = images_info
        return images

    def save_article_to_file(self, article_details: Dict[str, Any], article_id: str):
        """
        Saves the article's details into a file in the Medium folder.

        Args:
            article_details (Dict[str, str]): The details of the article to save.
            article_id (str): The unique ID of the article.
        """
        file_name = f"database/Medium/{article_id}.json"  

        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(article_details, file, ensure_ascii=False, indent=4)


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
