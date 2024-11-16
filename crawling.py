from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from fake_useragent import UserAgent
import requests
import json
import os

edition_link = "https://edition.cnn.com/"

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created.")
    else:
        print(f"Folder '{folder_name}' already exists.")

def get_web_stats(url):
    driver = webdriver.Chrome()
    driver.get(url)
    sleep(3)
    content = driver.page_source
    return content

def get_edition_post_links():
    content = get_web_stats(edition_link)
    soup = BeautifulSoup(content, 'html.parser')
    post_links = [edition_link + a['href'] for a in soup.select('.container__link')]
    return post_links

def save_post_data_to_json(post_data, filename):

    create_folder("CNN")

    file_path = os.path.join("CNN", filename)

    with open("CNN/" + filename, 'w', encoding='utf-8') as json_file:
        json.dump(post_data, json_file, ensure_ascii=False, indent=4)
    print(f"Post data has been saved to {filename}")

def scrape_post(url):
    user_agent = UserAgent()
    headers = {'User-Agent': user_agent.random}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    post_data = {}

    script_tag = soup.find('script', text=lambda t: t and "pageStellarId" in t)
    if script_tag:
        script_content = script_tag.string
        start_index = script_content.find("pageStellarId: '") + len("pageStellarId: '")
        end_index = script_content.find("'", start_index)
        post_data["pageStellarId"] = script_content[start_index:end_index]
    else:
        post_data["pageStellarId"] = None

    post_data["url"] = url

    title_tag = soup.find('title')
    post_data["title"] = title_tag.get_text(strip=True)

    publish_date_tag = soup.find('meta', {'property': 'article:published_time'})
    post_data["publish_date"] = publish_date_tag['content']

    last_update_tag = soup.find('meta', {'property': 'article:modified_time'})
    post_data["last_update_date"] = last_update_tag['content']

    ld_json_tag = soup.find('script', {'type': 'application/ld+json'})
    if ld_json_tag:
        ld_json_data = json.loads(ld_json_tag.string)  
        for item in ld_json_data:
            if item.get('@type') == 'NewsArticle':
                post_data["content"] = item.get('articleBody', None)

    images_info = []
    img_tags = soup.find_all('img')
    if img_tags:
        for img_tag in img_tags:
            image_url = img_tag.get('src')
            image_alt = img_tag.get('alt')
            if image_url and image_alt:
                images_info.append({
                    "image_url": image_url,
                    "image_alt": image_alt
                })
    post_data["images"] = images_info

    save_post_data_to_json(post_data, post_data['pageStellarId'] + ".json")

scrape_post("https://edition.cnn.com/2024/11/13/style/kiana-hayeri-snap-teenage-girls-afghanistan/index.html")


