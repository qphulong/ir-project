import sys
import os
from typing import List, Dict, Any

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)
from .cnn_crawler import CNNSearcher
#from database.medium_crawler import MediumScraper
from dotenv import load_dotenv

load_dotenv(dotenv_path=f"{SYSTEM_PATH}/backend/.env")
# API_KEY = os.getenv("RAPID_API_KEY")

class Indexer:
    def __init__(self):
        self.cnn_searcher = CNNSearcher()
        self.content_items: List[str] = []
        self.metadata_items: List[Dict[str, Any]] = []
        self.image_items: List[List[str]] = []
        # self.medium_crawler = MediumScraper(api_key=API_KEY)

    def crawl_and_index_cnn(self, keyword: str, n: int) -> None:
        cnn_document = self.cnn_searcher.search_posts(keyword=keyword, size=n)
        for document in cnn_document:
            self.content_items.append(document.get("content", ""))
            id = document.get("id", "")
            self.image_items.append(document.get("images", []))
            metadata = document.get("metadata", {})
            if isinstance(metadata, dict):
                self.add_metadata(id, metadata)
    
    def crawl_and_index_medium(self, keyword: str, n: int) -> None:
        medium_documents = self.medium_crawler.scrape_and_save_top_k_articles(keyword=keyword, k = n)
        medium_content = "\n".join([value['content'] for key, value in medium_documents["content"].items()])
        return medium_content
    
    def crawl_both(self, keyword: str, n_cnn: int, n_medium: int):
        cnn_documents = self.crawl_and_index_cnn(keyword, n_cnn)
        #medium_documents = self.crawl_and_index_medium(keyword, n_medium)
        return None
    
    def add_metadata(self, id: str, metadata: Dict[str, Any]) -> None:
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



        
    
