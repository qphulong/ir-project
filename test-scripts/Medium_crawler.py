import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from database import MediumScraper
from dotenv import load_dotenv

load_dotenv(dotenv_path=f"{SYSTEM_PATH}/backend/.env")

API_KEY = os.getenv("RAPID_API_KEY")
scraper = MediumScraper(api_key=API_KEY)
query = input("Enter search query (keyword): ")
top_k = int(input("Enter the number of top articles to fetch: "))
scraper.scrape_and_save_articles(keyword=query, k=top_k)