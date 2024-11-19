from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from fake_useragent import UserAgent
import requests
import json
import os
from typing import List, Optional, Dict, Any

edition_link = "https://edition.cnn.com/"


class CNNCrawler:
    """
    A class to scrape and save detailed post data from CNN articles.

    Attributes:
        output_dir (str): The directory where scraped data will be saved.

    Methods:
        create_folder():
            Creates the output directory if it doesn't exist.
        
        scrape_post(url: str):
            Scrapes data from a given CNN article URL and saves it to a JSON file.

        extract_page_stellar_id(soup: BeautifulSoup) -> Optional[str]:
            Extracts the unique pageStellarId from the article's script tags.

        extract_title(soup: BeautifulSoup) -> Optional[str]:
            Extracts the title of the article.

        extract_author_profile(soup: BeautifulSoup) -> Optional[str]:
            Extracts the link to the author's profile from the byline.

        extract_meta_content(soup: BeautifulSoup, property_name: str) -> Optional[str]:
            Extracts metadata content, such as publication or last update time.

        extract_article_body(soup: BeautifulSoup) -> Optional[str]:
            Extracts the main content or body of the article.

        extract_images(soup: BeautifulSoup) -> List[Dict[str, str]]:
            Extracts information about images in the article, including URLs and alt text.

        save_post_data_to_json(post_data: Dict[str, Any], filename: str):
            Saves the scraped article data to a JSON file in the output directory.
    """
    def __init__(self, output_dir: str = "database/CNN"):
        self.output_dir = output_dir
        self.user_agent = UserAgent()

    def create_folder(self) -> None:
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def scrape_post(self, url: str) -> None:
        headers = {'User-Agent': self.user_agent.random}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve {url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        post_data: Dict[str, Any] = {
            "url": url,
            "pageStellarId": self.extract_page_stellar_id(soup),
            "title": self.extract_title(soup),
            "author_profile": self.extract_author_profile(soup),
            "publish_date": self.extract_meta_content(soup, 'article:published_time'),
            "last_update_date": self.extract_meta_content(soup, 'article:modified_time'),
            "content": self.extract_article_paragraphs(soup),
            "images": self.extract_images(soup),
        }

        filename = f"{post_data.get('pageStellarId', 'default')}.json"
        self.save_post_data_to_json(post_data, filename)

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

    def extract_author_profile(self, soup: BeautifulSoup) -> Optional[str]:
        author_link_tag = soup.find('a', class_='byline__link')
        if author_link_tag:
            return author_link_tag['href'] 

        byline_names_div = soup.find('div', class_='byline__names')
        if byline_names_div:
            name_span = byline_names_div.find('span', class_='byline__name')
            if name_span:
                return name_span.get_text(strip=True)
        
        return None

    def extract_meta_content(self, soup: BeautifulSoup, property_name: str) -> Optional[str]:
        meta_tag = soup.find('meta', {'property': property_name})
        return meta_tag['content'] if meta_tag else None

    def extract_article_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        paragraphs = []
        paragraph_tags = soup.find_all('p', class_='paragraph inline-placeholder vossi-paragraph')
        if not paragraph_tags:
            fallback_div = soup.find('div', class_='video-resource__description')
            if fallback_div:
                paragraph_tags = fallback_div.find_all('p')  
        for p_tag in paragraph_tags:
            text = p_tag.get_text(strip=True)
            if text:  
                paragraphs.append(text)
        return paragraphs

    def extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        images_info = []
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            image_url = img_tag.get('src')
            image_alt = img_tag.get('alt')
            if image_url and image_alt:
                images_info.append({
                    "image_url": image_url,
                    "image_alt": image_alt
                })
        return images_info

    def save_post_data_to_json(self, post_data: Dict[str, Any], filename: str) -> None:
        self.create_folder()
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(post_data, json_file, ensure_ascii=False, indent=4)


class CNNLinkGetter:
    """
    A class to retrieve links to articles from the CNN homepage.

    Attributes:
        base_url (str): The base URL of the CNN homepage.

    Methods:
        get_web_stats(url: str) -> str:
            Opens the given URL in a browser, retrieves, and returns the page source.

        get_CNN_post_links(limit: int = 100) -> List[str]:
            Extracts and returns a list of article links from the CNN homepage.
    """
    def __init__(self, base_url: str = "https://edition.cnn.com/"):
        self.base_url = base_url

    def get_web_stats(self, url: str) -> str:
        driver = webdriver.Chrome()
        try:
            driver.get(url)
            sleep(3)
            return driver.page_source
        finally:
            driver.quit()

    def get_CNN_post_links(self, limit: int = 100) -> List[str]:
        content = self.get_web_stats(self.base_url)
        soup = BeautifulSoup(content, 'html.parser')

        post_links = []
        for a in soup.select('a.container__link'):
            href = a.get('href')
            if href:
                full_url = href if href.startswith('http') else self.base_url.rstrip('/') + href
                post_links.append(full_url)

            if len(post_links) >= limit:
                break

        return post_links

if __name__ == "__main__":
    CNN = CNNLinkGetter()
    links = CNN.get_CNN_post_links(limit=100)
    crawler = CNNCrawler()

    for link in links:
        crawler.scrape_post(link)
