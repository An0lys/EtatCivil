from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os

def getdata(url):
    session = HTMLSession()
    cookies = {'PHPSESSID': '28c715fbf355c19e5e3418315bb431e1'}
    r = session.get(url, cookies=cookies)
    r.html.render(timeout=20)  # Render the JavaScript
    return r, session

def get_image_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        if 'https://archives.paris.fr/arkotheque/visionneuse/img_prot.php' in img_tag.get('src', ''):
            img_url = img_tag['src']
    return img_url

def extract_image_url(url):
    r, session = getdata(url)
    url = get_image_url(r.html.html)
    session.close()
    return url

def download_image(img_url, save_path):
    cookies = {'PHPSESSID': '28c715fbf355c19e5e3418315bb431e1'}
    img_data = requests.get(img_url, cookies=cookies).content
    with open(save_path, 'wb') as handler:
        handler.write(img_data)

# Read URLs from urls.csv
urls_df = pd.read_csv('urls.csv')
img_urls = []

if not os.path.exists('data'):
    os.makedirs('data')

for url in urls_df['urls']:
    print("Scraping image URL from", url)
    img_url = extract_image_url(url)
    print(img_url)
    img_urls.append(img_url)
    if img_url:
        img_name = os.path.join('data', img_url.split('/')[-1].split('&')[0])
        download_image(img_url, img_name)

# Save image URLs to imgs_url.csv
img_urls_df = pd.DataFrame(img_urls, columns=['url'])
img_urls_df.to_csv('imgs_url.csv', index=False)