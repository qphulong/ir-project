import sys
import os
from typing import List, Dict, Any

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)
from .cnn_crawler import CNNSearcher
from database.medium_crawler import MediumScraper
from dotenv import load_dotenv

load_dotenv(dotenv_path=f"{SYSTEM_PATH}/backend/.env")
API_KEY = os.getenv("RAPID_API_KEY")

class Indexer:
    """
    The Indexer class is responsible for crawling content from CNN and Medium,
    processing the crawled data, and organizing it into structured lists for
    further use. It supports crawling both CNN and Medium articles based on
    a given keyword and size limit.
    """
    def __init__(self):
        self.cnn_searcher = CNNSearcher()
        self.content_items: List[str] = []
        self.metadata_items: List[Dict[str, Any]] = []
        self.image_items: List[List[str]] = []
        if not API_KEY:
            print("RAPID_API_KEY is missing. Medium crawling functionality will be disabled.")
            self.medium_crawler = None
        else:
            self.medium_crawler = MediumScraper(api_key=API_KEY)

    def crawl_and_index_cnn(self, keyword: str, n: int) -> None:
        """
        Crawls CNN articles based on a keyword and stores the content, images, and metadata.

        Args:
            keyword (str): The keyword to search for in CNN articles.
            n (int): The number of articles to crawl.
        """
        cnn_document = self.cnn_searcher.search_posts(keyword=keyword, size=n)
        for document in cnn_document:
            self.content_items.append(document.get("content", ""))
            id = document.get("id", "")
            self.image_items.append(document.get("images", []))
            metadata = document.get("metadata", {})
            if isinstance(metadata, dict):
                self.add_metadata(id, metadata)
    
    def crawl_and_index_medium(self, keyword: str, n: int) -> None:
        """
        Crawls Medium articles based on a keyword and stores the content, images, and metadata.

        Args:
            keyword (str): The keyword to search for in Medium articles.
            n (int): The number of articles to crawl.
        """
        if not self.medium_crawler:
            print("Medium crawling is disabled because RAPID_API_KEY is missing.")
            return
        medium_documents = self.medium_crawler.scrape_and_save_top_k_articles(keyword=keyword, k = n)
        for document in medium_documents:
            self.content_items.append(document.get("content", ""))
            id = document.get("id", "")
            self.image_items.append(document.get("images", []))
            metadata = document.get("metadata", {})
            if isinstance(metadata, dict):
                self.add_metadata(id, metadata)
        
    
    def crawl_both(self, keyword: str, n_cnn: int, n_medium: int):
        """
        Crawls both CNN and Medium articles and indexes their content.

        Args:
            keyword (str): The keyword to search for in articles.
            n_cnn (int): The number of CNN articles to crawl.
            n_medium (int): The number of Medium articles to crawl.
        """
        self.crawl_and_index_cnn(keyword, n_cnn)
        self.crawl_and_index_medium(keyword, n_medium)
    
    def add_metadata(self, id: str, metadata: Dict[str, Any]) -> None:
        """
        Adds metadata with embeddings for a given document ID.

        Args:
            id (str): The unique identifier for the document.
            metadata (Dict[str, Any]): Metadata containing embeddings.
        """
        self.metadata_items.append({id: metadata[id]["embedding"]})
    
    def get_content_embeddings(self) -> List[str]:
        return self.content_items

    def get_images_items_embeddings(self) -> List[List[str]]:
        return self.image_items

    def get_metadata_items_embeddings(self) -> List[Dict[str, Any]]:
        return self.metadata_items
    
    def clear_data(self) -> None:
        self.content_items.clear()
        self.metadata_items.clear()
        self.image_items.clear()



        
    
