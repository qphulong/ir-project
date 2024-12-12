import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from database import CNNCrawler, CNNSearcher

keyword = input("Enter the search keyword: ")
size = int(input("Enter the number of results: "))
page_count = size // 10
searcher = CNNSearcher()
links = []
for page in range(1, page_count + 1):
    page_links = searcher.search(keyword=keyword, size=10, page=page, sort="newest")
    links.extend(page_links)
    if len(links) >= size:
        break

links = links[:size]
crawler = CNNCrawler()
for link in links:
    crawler.scrape_post(link)

'''
base_url = "https://edition.cnn.com/"
subnav_links = get_subnav_links(base_url)
filtered_links = [link for link in subnav_links if "about" not in link]
filtered_links.append(base_url)
links = []
crawler = CNNCrawler()
for link in filtered_links:
    CNN = CNNLinkGetter(link)
    links = CNN.get_CNN_post_links(limit=10000000000)
    for link in links:
        crawler.scrape_post(link)
'''
'''
crawler = CNNCrawler()
crawler.scrape_post("https://edition.cnn.com/2024/12/03/asia/south-korea-martial-law-explainer-intl-hnk/index.html")
'''