import requests  
from bs4 import BeautifulSoup  
import pandas as pd

def getdata(url):  
    session = requests.Session()
    session.cookies.set('PHPSESSID', 'ffa4ace44fbe96f1789d0d40ced39ae4')
    r = session.get(url)  
    return r.text

df = pd.DataFrame(columns=['url'])

base_url = "https://archives.paris.fr"
for i in range(0, 501, 20):
    print("Scraping url", i)
    url = f"https://archives.paris.fr/s/4/etat-civil-actes/resultats/?&ref_fonds=4&debut={i}"
    htmldata = getdata(url)
    soup = BeautifulSoup(htmldata, 'html.parser')  
    links = soup.find_all('a', href=True)
    for link in links:
        if 'href' in link.attrs and link['href'].startswith("javascript:ArkVisuImage"):
            inner_link = link['href'].split("\'")[1]
            full_url = base_url + inner_link
            df = pd.concat([df, pd.DataFrame({'url': [full_url]})], ignore_index=True)

df['Arrondissement'] = 4
df['Type'] = 'Death'
df.to_csv('urls.csv', mode='a', header=False, index=False)