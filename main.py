import pandas as pd
import os
import requests

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Define the cookie
cookies = {'PHPSESSID': '28c715fbf355c19e5e3418315bb431e1'}

# Read the CSV file
df = pd.read_csv('imgs_url.csv')
for img_url in df['url']:
    img_name = os.path.basename(img_url)
    img_path = os.path.join('data', img_name)

    # Download the image
    response = requests.get(img_url, cookies=cookies)
    if response.status_code == 200:
        with open(img_path, 'wb') as img_file:
            img_file.write(response.content)
        print(f"Downloaded {img_name}")
    else:
        print(f"Failed to download {img_url}")