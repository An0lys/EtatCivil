from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import base64

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

if not os.path.exists('data'):
    os.makedirs('data')

for i in range(0, 198401+200):
    url = "https://archives.paris.fr/arkotheque/arkotheque_visionneuse_archives.php?arko=" + base64.b64encode('a:4:{s:4:"date";s:10:"2025-03-26";s:10:"type_fonds";s:11:"arko_seriel";s:4:"ref1";i:4;s:4:"ref2";i:'+i+';}').decode('utf-8')
    print("Scraping image URL from", url)
    img_url = extract_image_url(url)
    print(img_url)
    if img_url:
        img_name = os.path.join('data', img_url.split('/')[-1].split('&')[0])
        download_image(img_url, img_name)