import requests  
from bs4 import BeautifulSoup  
import pandas as pd

def getdata(url):  
    session = requests.Session()
    session.cookies.set('PHPSESSID', '28c715fbf355c19e5e3418315bb431e1')
    r = session.get(url)  
    return r.text

df = pd.DataFrame(columns=['url'])

base_url = "https://archives.paris.fr"
for i in range(0, 501, 20):
    print("Scraping url", i)
    url = f"https://archives.paris.fr/s/5/etat-civil-reconstitue-fichiers/resultats/?&ref_fonds=5&debut={i}"
    htmldata = getdata(url)
    soup = BeautifulSoup(htmldata, 'html.parser')  
    links = soup.find_all('a', href=True)
    for link in links:
        if 'href' in link.attrs and link['href'].startswith("javascript:ArkVisuImage"):
            inner_link = link['href'].split("\'")[1]
            full_url = base_url + inner_link
            df = pd.concat([df, pd.DataFrame({'url': [full_url]})], ignore_index=True)

df.to_csv('urls.csv', index=False)