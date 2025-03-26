import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL de la page de résultats où se trouvent les liens relatifs
results_url = "https://archives.paris.fr/s/4/etat-civil-actes/resultats/"

# Création du dossier "DOC" s'il n'existe pas
folder = "DOC"
if not os.path.exists(folder):
    os.makedirs(folder)

# Récupération du contenu de la page de résultats
response = requests.get(results_url)
if response.status_code != 200:
    print("Erreur lors de la récupération de la page :", results_url)
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# Recherche des liens relatifs correspondant au pattern demandé
# On cherche des liens qui commencent par /arkotheque/visionneuse/visionneuse.php?arko=
pattern = re.compile(r"^/arkotheque/visionneuse/visionneuse\.php\?arko=")
anchors = soup.find_all("a", href=pattern)

if not anchors:
    print("Aucun lien correspondant n'a été trouvé sur la page.")
    
downloaded = 0

# Pour chaque lien trouvé, on construit l'URL complète et on traite la page visionneuse
for index, a in enumerate(anchors, start=1):
    relative_link = a.get("href")
    # Compléter l'URL relative avec le domaine
    full_url = urljoin("https://archives.paris.fr", relative_link)
    print("Traitement de :", full_url)
    
    try:
        # Récupération de la page visionneuse
        vis_response = requests.get(full_url)
        if vis_response.status_code != 200:
            print("Erreur lors de la récupération de :", full_url)
            continue

        vis_soup = BeautifulSoup(vis_response.text, "html.parser")
        # Recherche de la première balise <img> dans la page
        img_tag = vis_soup.find("img")
        if not img_tag:
            print("Aucune image trouvée sur la page :", full_url)
            continue

        img_src = img_tag.get("src")
        if not img_src:
            print("Balise <img> sans attribut src sur la page :", full_url)
            continue

        # Transformation de l'URL de l'image en URL absolue si nécessaire
        img_url = urljoin(full_url, img_src)
        print("Image trouvée :", img_url)

        # Téléchargement de l'image
        img_download = requests.get(img_url)
        if img_download.status_code != 200:
            print("Erreur lors du téléchargement de l'image :", img_url)
            continue

        # Détermination du nom de fichier (extrait de l'URL ou généré)
        filename = os.path.basename(img_src)
        if not filename:
            filename = f"image_{index}.jpg"
        filepath = os.path.join(folder, filename)

        with open(filepath, "wb") as f:
            f.write(img_download.content)
        downloaded += 1
        print("Téléchargé :", filepath)

    except Exception as e:
        print("Erreur pour l'URL", full_url, ":", e)

print(f"Nombre total d'images téléchargées : {downloaded}")
