from splinter import Browser
import time
import os
import pandas as pd
import requests
import base64


def get_request_headers(browser, url):
    cookies = browser.cookies.all() # Get the cookies from the browser
    headers = {
        'User-Agent': browser.driver.execute_script("return navigator.userAgent;"), # Get the user-agent from the browser
        'Referer': url.split('#')[0], # Get the referer from the URL
    }
    return cookies, headers

def download_image(url, data_dir, cookies, headers):
    path = os.path.join(data_dir, img_url.split('/')[-1].split('=')[1].split('&')[0])
    response = requests.get(img_url, cookies=cookies, headers=headers)
    if response.status_code != 200:
        print("Error", response.status_code)
    with open(path, "wb") as file:
        file.write(response.content)

# Where to save the images
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

# Main loop
browser = Browser('chrome')
img_urls = []
for i in range(198401, 198401+200):
    to_encode = 'a:4:{s:4:"date";s:10:"2025-03-26";s:10:"type_fonds";s:11:"arko_seriel";s:4:"ref1";i:4;s:4:"ref2";i:'+str(i)+';}'
    url = "https://archives.paris.fr/arkotheque/arkotheque_visionneuse_archives.php?arko=" + base64.b64encode(to_encode.encode()).decode('utf-8')
    print("Scraping from", url)
    browser.visit(url)
    is_last_page = False
    while not is_last_page:
        time.sleep(1) # Wait for the image to load
        img_url = browser.find_by_id("image1")['src']
        print(" > ", img_url)
        img_urls.append(img_url)
        cookies, headers = get_request_headers(browser, url)
        download_image(img_url, data_dir, cookies, headers) # Download the image
        next_button = browser.find_by_id("arkoVision_next")
        next_button.click() # Go to next image
        is_last_page = 'desactive' in next_button['class'] # Check the class of the next button to know if we are on the last page
    print(f"{len(img_urls)} images downloaded so far\n")
browser.driver.close() # close the window