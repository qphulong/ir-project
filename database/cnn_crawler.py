from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import os
import sys
import math
from typing import List, Optional, Dict, Any,  Optional
from datetime import datetime
from dotenv import load_dotenv
SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=f"{SYSTEM_PATH}/backend/.env")
sys.path.append(SYSTEM_PATH)
from backend.utils import binary_quantized, binary_array_to_base64, float32_vector_to_base64
from backend.semantice_chunker import SemanticChunker
from backend.nomic_embed import NomicEmbed
from backend.nomic_embed_vision import NomicEmbedVision
from llama_index.core.schema import Document as LlamaIndexDocument
from concurrent.futures import ThreadPoolExecutor, as_completed

num_of_no_id_post = 1

class Driver:
    def __init__(self):
        self.driver_pool = []

    def create_driver(self):
        ua = UserAgent()
        user_agent = ua.random
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Chrome(options=options)

        return driver
    
    def get_driver(self):
        if len(self.driver_pool) > 0:
            return self.driver_pool.pop()
        else:
            return self.create_driver()
        
    def release_driver(self, driver):
        self.driver_pool.append(driver)


class CNNCrawler:
    """
    A class for scraping and saving detailed post data from CNN articles, including metadata, content, images, and embeddings.

    Attributes:
        output_dir (str): Directory where scraped data will be saved.
        visited_links_file (str): File to store visited URLs.
        visited_links (set): Tracks visited links to avoid re-scraping.
        max_depth (int): Maximum depth for crawling related articles.

    Methods:
        load_visited_links() -> set:
            Loads previously visited links from a file.

        save_visited_links() -> None:
            Saves the visited links to a file.

        create_folder() -> None:
            Creates the output directory if it does not exist.

        format_date(iso_date: str) -> str:
            Converts an ISO date string to a human-readable format (DD/MM/YYYY).

        get_embed_text(text: str) -> str:
            Generates a binary quantized embedding for text and encodes it as Base64.

        get_embed_img(img_url: str) -> str:
            Generates an embedding for an image URL and encodes it as Base64.

        scrape_post(url: str) -> None:
            Scrapes an article from CNN, extracts metadata, content, and embeddings, 
            and saves the data to a JSON file.

        extract_page_stellar_id(soup: BeautifulSoup) -> Optional[str]:
            Extracts the unique pageStellarId from script tags in the article's HTML.

        extract_title(soup: BeautifulSoup) -> Optional[str]:
            Extracts the article's title.

        extract_author_profile_link(soup: BeautifulSoup) -> Optional[str]:
            Extracts the author's profile link.

        extract_author_name(soup: BeautifulSoup) -> Optional[str]:
            Extracts the author's name.

        extract_meta_content(soup: BeautifulSoup, property_name: str) -> Optional[str]:
            Extracts specific metadata (e.g., publication time) by property name.

        extract_article_paragraphs(soup: BeautifulSoup, ID: str) -> Dict[str, Dict[str, Any]]:
            Extracts paragraphs from the article and generates embeddings for each.

        extract_images(soup: BeautifulSoup, ID: str) -> List[Dict[str, str]]:
            Extracts image URLs, alt text, and generates embeddings for each image.

        extract_srt(soup: BeautifulSoup, ID: str) -> List[Dict[str, str]]:
            Extracts subtitles in SRT format, if available, and processes them into chunks.

        get_text_from_srt(url: str) -> str:
            Downloads and parses an SRT file into plain text.

        save_post_data_to_json(post_data: Dict[str, Any], filename: str) -> None:
            Saves scraped article data to a JSON file in the output directory.
    """
    def __init__(self, output_dir: str = "resources/quantized-db", visited_links_file="visited_links.json"):
        self.output_dir = output_dir
        self.user_agent = UserAgent()
        self.visited_links_file = visited_links_file
        self.visited_links = self.load_visited_links()
        self.text_embed_model = NomicEmbed()
        self.vision_embed_model = NomicEmbedVision()
        self.semantic_chunker = SemanticChunker(breakpoint_percentile_threshold=60)
        self.driver = Driver()

    def load_visited_links(self) -> set:
        if os.path.exists(self.visited_links_file):
            with open(self.visited_links_file, "r") as file:
                return set(json.load(file))
        return set()
    
    def save_visited_links(self) -> None:
        with open(self.visited_links_file, "w") as file:
            json.dump(list(self.visited_links), file)

    def create_folder(self) -> None:
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def format_date(self, iso_date: str) -> str:
        if iso_date is None:
            return "Invalid date" 
        try:
            datetime_obj = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            return datetime_obj.strftime("%d/%m/%Y")
        except ValueError:
            return iso_date
    
    def get_embed_text(self, text: str) ->str:
        embedding = self.text_embed_model.get_text_embedding(text)
        embedding = binary_quantized(embedding)
        return binary_array_to_base64(embedding)
    
    def get_embed_img(self, img_url:str)->str:
        img_embedding = self.vision_embed_model.embed_image(img_url)
        return float32_vector_to_base64(img_embedding)


    def scrape_post(self, url: str) -> None:
        if url in self.visited_links:
           return
        
        global num_of_no_id_post
        try:
            driver = self.driver.get_driver()

            driver.get(url)
        
            WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )
        
            page_source = driver.page_source
        except Exception as e:
            print(f"Error retrieving dynamic content from {url}: {e}")
            self.visited_links.add(url)
            self.save_visited_links()
            return
        finally:
            self.driver.release_driver(driver)

        soup = BeautifulSoup(page_source, 'html.parser')

        stellar_id = self.extract_page_stellar_id(soup)

        id = "cnn_" + stellar_id if stellar_id else "None"

        publish_date = self.extract_meta_content(soup, 'article:published_time')

        last_update_date = self.extract_meta_content(soup, 'article:modified_time')

        metadata: Dict[str, Any] = {
            "url": url,
            "pageStellarId": self.extract_page_stellar_id(soup),
            "author_url": self.extract_author_profile_link(soup),
            id:  {
                "title": self.extract_title(soup),
                "author": self.extract_author_name(soup),
                "publish_date": self.format_date(publish_date),
                "last_update_date": self.format_date(last_update_date),
            }
        }

        embedding =""
        for key, value in metadata[id].items():
            embedding += f"{key}: {value}\n"

        metadata[id]["embedding"] = self.get_embed_text(embedding)

        content_key = "content"

        post_data: Dict[str, Any] = {
            "id": id,
            "metadata": metadata,
            content_key: self.extract_srt(soup, id) if "/videos/" in url or "/video/" in url else self.extract_article_paragraphs(soup, id),
            "images": self.extract_images(soup, id) if not "/videos/" in url and not "/video/" in url else {},
        }

        if post_data.get('pageStellarId', 'default') == None:
            filename = f"None_{num_of_no_id_post}.json"
            num_of_no_id_post += 1
        else:
            filename = f"{post_data.get('id', 'default')}.json"
        self.save_post_data_to_json(post_data, filename)

        self.visited_links.add(url)
        self.save_visited_links()

        return post_data
        

    def extract_page_stellar_id(self, soup: BeautifulSoup) -> Optional[str]:
        script_tag = soup.find('script', text=lambda t: t and "pageStellarId" in t)
        if script_tag:
            script_content = script_tag.string
            start_index = script_content.find("pageStellarId: '") + len("pageStellarId: '")
            end_index = script_content.find("'", start_index)
            return script_content[start_index:end_index]
        return None

    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else None

    def extract_author_profile_link(self, soup: BeautifulSoup) -> Optional[str]:
        author_link_tag = soup.find('a', class_='byline__link')
        if author_link_tag:
            return author_link_tag['href']
        return None

    def extract_author_name(self, soup: BeautifulSoup) -> Optional[str]:
        byline_names_div = soup.find('div', class_='byline__names')
        if byline_names_div:
            name_span = byline_names_div.find('span', class_='byline__name')
            if name_span:
                return name_span.get_text(strip=True)
        return None

    def extract_meta_content(self, soup: BeautifulSoup, property_name: str) -> Optional[str]:
        meta_tag = soup.find('meta', {'property': property_name})
        return meta_tag['content'] if meta_tag else None

    def extract_article_paragraphs(self, soup: BeautifulSoup, ID: str) -> Dict[str, Dict[str, Any]]:
        paragraphs: Dict[str, Any] = {}
        paragraph_tags = soup.find_all('p', class_='paragraph inline-placeholder vossi-paragraph')
        if not paragraph_tags:
            paragraph_tags = soup.find_all('p', class_='paragraph inline-placeholder vossi-paragraph-primary-core-light')
        if not paragraph_tags:
            fallback_div = soup.find('div', class_='video-resource__description')
            if fallback_div:
                paragraph_tags = fallback_div.find_all('p')

        merged_text = "\n".join(p_tag.get_text(strip=True) for p_tag in paragraph_tags if p_tag.get_text(strip=True))

        document =  LlamaIndexDocument(text=merged_text)

        nodes = self.semantic_chunker.chunk_nodes_from_documents([document])
        
        for i, node in enumerate(nodes, start=1):
            text = node.text.strip()
            if text:
                paragraph: Dict[str, Any] = {
                    "content": text,
                    "embedding": self.get_embed_text(text)
                }
                key = f"{ID}_text_{i}"
                paragraphs[key] = paragraph

        return paragraphs

    def extract_images(self, soup: BeautifulSoup, ID:str) -> List[Dict[str, str]]:
        images_infos : Dict[str, Any] = {}
        img_tags = soup.find_all('img', class_='image__dam-img')
        for i,img_tag in enumerate(img_tags, start=1):
            if img_tag.find_parent(class_='related-content') or img_tag.find_parent(class_='video-resource__image') or img_tag.find_parent(class_='container__item-media') or img_tag.find_parent(class_='image__related-content'):
                continue
            image_url = img_tag.get('src')
            image_alt = img_tag.get('alt')
            if image_url and image_alt and "http" in image_url:
                images_info : Dict[str, Any] = {
                    "image_url":image_url,
                    "image_alt": image_alt,
                    "embedding" : self.get_embed_img(image_url)
                }
                key = f"{ID}_image_{i}"
                images_infos[key] = images_info
        return images_infos
    
    def extract_srt(self, soup: BeautifulSoup, ID: str) -> List[Dict[str, str]]:
        paragraphs: Dict[str, Any] = {}
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            try:
                data = json.loads(script_tag.string)

                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "caption" in item:
                            captions = item["caption"]
                            for caption in captions:
                                if caption.get("encodingFormat") == "srt":
                                    url = caption.get("url")
                                    subtitle = self.get_text_from_srt(url)
                                    document =  LlamaIndexDocument(text=subtitle)
                                    nodes = self.semantic_chunker.chunk_nodes_from_documents([document])
                                    for i, node in enumerate(nodes, start=1):
                                        text = node.text.strip()
                                        if text:
                                            paragraph: Dict[str, Any] = {
                                                "content": text,
                                                "embedding": self.get_embed_text(text)
                                            }
                                            key = f"{ID}_text_{i}"
                                            paragraphs[key] = paragraph
                                    return paragraphs
                elif isinstance(data, dict):
                    captions = data.get("caption", [])
                    for caption in captions:
                        if caption.get("encodingFormat") == "srt":
                            url = caption.get("url")
                            subtitle = self.get_text_from_srt(url)
                            document =  LlamaIndexDocument(text=subtitle)
                            nodes = self.semantic_chunker.chunk_nodes_from_documents([document])
                            for i, node in enumerate(nodes, start=1):
                                text = node.text.strip()
                                if text:
                                    paragraph: Dict[str, Any] = {
                                        "content": text,
                                        "embedding": self.get_embed_text(text)
                                    }
                                    key = f"{ID}_text_{i}"
                                    paragraphs[key] = paragraph
                            return paragraphs
            except json.JSONDecodeError:
                return None
        return None
    
    def get_text_from_srt(self, url: str) -> str:
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Failed to download the SRT file")

        lines = response.text.splitlines()

        text = []
        for line in lines:
            if "-->" not in line and line.strip() and not line.strip().isdigit():
                text.append(line.strip())

        return " ".join(text)

    def save_post_data_to_json(self, post_data: Dict[str, Any], filename: str) -> None:
        self.create_folder()
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(post_data, json_file, ensure_ascii=True, indent=4)

class CNNSearcher:
    """
    A class to search the CNN website and retrieve article or video links based on keywords.

    Attributes:
        base_url (str): The CNN search page URL (default: 'https://edition.cnn.com/search').
        scrawler (CNNCrawler): Handles scraping content from individual posts.

    Methods:
        search(keyword: str, size: int = 10, page: int = 1, sort: str = "newest") -> List[str]:
            Retrieves a list of article or video URLs for a given keyword with optional pagination and sorting.

        search_posts(keyword: str, size: int = 10, max_workers: int = os.cpu_count() * 2) -> List[dict]:
            Fetches and parses search results for a keyword, returning content as a list of dictionaries.
    """
    def __init__(self, base_url: str = "https://edition.cnn.com/search"):
        self.base_url = base_url
        self.scrawler =  CNNCrawler()

    def search(self, keyword: str, size: int = 10, page: int = 1, sort: str = "newest") -> List[str]:
        start_index = (page - 1) * size
        
        search_url = f"{self.base_url}?q={keyword}&from={start_index}&size={size}&page={page}&sort={sort}&types=all&section="
        
        ua = UserAgent()
        user_agent = ua.random

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(search_url)

            driver.implicitly_wait(3)

            result_links = []
            elements = driver.find_elements(By.CSS_SELECTOR, "a.container__link")
            for element in elements:
                href = element.get_attribute("href")
                if href:
                    full_url = href if href.startswith("http") else f"https://edition.cnn.com{href}"
                    if full_url not in result_links and "/live-news/" not in full_url:
                        result_links.append(full_url)
            return result_links
        finally:
            driver.quit()

    def search_posts(self, keyword: str, size: int = 10, max_workers: int = os.cpu_count() * 2):
        links = []
        page_count = math.ceil(size / 10)

        for page in range(1, page_count + 1):
            current_size = min(size - len(links), 10)
            page_links = self.search(keyword=keyword, size=current_size, page=page, sort="newest")
            links.extend(page_links)
            if len(links) >= size:
                break

        links = links[:size]

        contents = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_link = {executor.submit(self.scrawler.scrape_post, link): link for link in links}
            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    content = future.result()
                    if content:
                        contents.append(content)
                except Exception as e:
                    print(f"Error processing {link}: {e}")

        return contents