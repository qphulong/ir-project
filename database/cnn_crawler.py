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
from backend.utils import *
from backend import NomicEmbedVision, NomicEmbed, SemanticChunker
from llama_index.core.schema import Document as LlamaIndexDocument

num_of_no_id_post = 1


class CNNCrawler:
    """
    A class to scrape and save detailed post data from CNN articles.

    Attributes:
        output_dir (str): The directory where scraped data will be saved.
        visited_links_file (str): The filename to store visited URLs.
        visited_links (set): A set to keep track of visited links to avoid re-scraping.
        max_depth (int): The maximum depth to crawl for related articles.

    Methods:
        load_visited_links() -> set:
            Loads previously visited links from the visited links file.

        save_visited_links() -> None:
            Saves the current set of visited links to the visited links file.

        create_folder() -> None:
            Ensures the output directory exists.

        format_date(iso_date: str) -> str:
            Converts ISO date strings to a human-readable format (DD/MM/YYYY).

        get_embed_text(text: str) -> str:
            Generates a binary quantized embedding for the given text and encodes it as Base64.

        get_embed_img(img_url: str) -> str:
            Generates an embedding for an image given its URL and encodes it as Base64.

        scrape_post(url: str, current_depth: int = 0) -> None:
            Scrapes an article from CNN, extracts metadata, content, and embeddings, 
            and saves the data to a JSON file.

        scrape_related_links(soup: BeautifulSoup, current_depth: int) -> None:
            Extracts and recursively scrapes related article links from a given page.

        extract_page_stellar_id(soup: BeautifulSoup) -> Optional[str]:
            Extracts the unique pageStellarId from the article's script tags.

        extract_title(soup: BeautifulSoup) -> Optional[str]:
            Extracts the article's title from the HTML.

        extract_author_profile(soup: BeautifulSoup) -> Optional[str]:
            Extracts the author's profile link or name from the article.

        extract_meta_content(soup: BeautifulSoup, property_name: str) -> Optional[str]:
            Extracts metadata content such as publication or update time.

        extract_article_paragraphs(soup: BeautifulSoup, ID: str) -> List[Dict[str, Any]]:
            Extracts paragraphs from the article body and generates embeddings for each.

        extract_images(soup: BeautifulSoup, ID: str) -> List[Dict[str, str]]:
            Extracts image URLs, alt text, and generates embeddings for each image.

        extract_srt(soup: BeautifulSoup) -> Optional[str]:
            Extracts and returns subtitles in SRT format if available in the article.

        get_text_from_srt(url: str) -> str:
            Downloads and parses SRT files from the given URL into plain text.

        save_post_data_to_json(post_data: Dict[str, Any], filename: str) -> None:
            Saves the scraped article data to a JSON file in the output directory.
    """
    def __init__(self, output_dir: str = "resources/test-big-database/database/CNN", visited_links_file="visited_links.json", max_depth=10):
        self.output_dir = output_dir
        self.user_agent = UserAgent()
        self.visited_links_file = visited_links_file
        self.visited_links = self.load_visited_links()
        self.text_embed_model = NomicEmbed()
        self.vision_embed_model = NomicEmbedVision()
        self.semantic_chunker = SemanticChunker(breakpoint_percentile_threshold=60)
        self.max_depth = max_depth

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
           print(f"visited{url}")
           return
        
        global num_of_no_id_post
        try:

            ua = UserAgent()
            user_agent = ua.random

            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument(f"user-agent={user_agent}")
            driver = webdriver.Chrome(options=options)
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
            driver.quit()

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
            "images": self.extract_images(soup, id) if not "/videos/" in url and not "/video/" in url else None,
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

        #self.scrape_related_links(soup, current_depth + 1)

    def scrape_related_links(self, soup: BeautifulSoup, current_depth: int) -> None:
        links = soup.find_all("a", href=True, class_="container__link")
        for link in links:
            href = link["href"]
            if href.startswith("http"):
                full_url = href
            elif href.startswith("/"):
                full_url = f"https://edition.cnn.com{href}"
            else:
                continue
            if full_url in self.visited_links:
                continue
            if not "/videos/" in href and not "/video/" in href:
                continue
            self.scrape_post(full_url, current_depth)
        

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

'''
class CNNLinkGetter:
    """
    A class to scrape CNN post links (including video links) from the homepage.
    
    Attributes:
        base_url (str): The base URL of the CNN website (default is 'https://edition.cnn.com').

    Methods:
        get_web_stats(url: str) -> str:
            Scrapes the web page content for a given URL using Selenium.
        
        get_CNN_post_links(limit: int = 100000) -> List[str]:
            Scrapes post links from the CNN homepage, including video links, up to a specified limit.
    """
    def __init__(self, base_url: str = "https://edition.cnn.com"):
        self.base_url = base_url

    def get_web_stats(self, url: str) -> str:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(url)
            return driver.page_source
        finally:
            driver.quit()

    def get_CNN_post_links(self, limit: int = 100000) -> List[str]:
        content = self.get_web_stats(self.base_url)
        soup = BeautifulSoup(content, 'html.parser')

        post_links = []
        for a in soup.select('a.container__link'):
            href = a.get('href')
            if href and "/videos/" in href or "/video/" in href:
                full_url = href if href.startswith('http') else ("https://edition.cnn.com").rstrip('/') + href
                post_links.append(full_url)

            if len(post_links) >= limit:
                break

        return post_links
    
def get_subnav_links(base_url: str) -> List[str]:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(base_url)
    
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            subnav_links = []
            for a_tag in soup.find_all('a', class_='subnav__section-link'):
                href = a_tag.get('href')
                if href:
                    full_url = href if href.startswith('http') else base_url.rstrip('/') + href
                    subnav_links.append(full_url)
    
            return subnav_links
        finally:
            driver.quit()
    '''

class CNNSearcher:
    """
    A class to interact with the CNN search page and retrieve links to search results.

    This class allows users to search for a specific keyword on the CNN website and retrieve
    a list of URLs of the articles or videos in the search results. It uses Selenium to scrape
    the search result page and fetch the URLs of the articles or videos.

    Attributes:
        base_url (str): The base URL for the CNN search page (default is 'https://edition.cnn.com/search').

    Methods:
        search(keyword: str, size: int = 10, page: int = 1, sort: str = "newest") -> List[str]:
            Searches CNN for the given keyword and returns a list of URLs of the search result articles.
            Supports pagination and sorting by date.
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

    def search_posts(self, keyword: str, size: int = 10):
        links = []
        page_count = math.ceil(size / 10)

        for page in range(1, page_count + 1):
            current_size = min(size - len(links), 10)
            page_links = self.search(keyword=keyword, size=current_size, page=page, sort="newest")
            links.extend(page_links)
            if len(links) >= size:
                break

        links = links[:size]

        contents = [self.scrawler.scrape_post(link) for link in links]

        return contents

    
    
