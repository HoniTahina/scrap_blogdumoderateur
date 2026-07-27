import time
import pandas as pd
import requests
from requests.exceptions import HTTPError, Timeout
from bs4 import BeautifulSoup
from datetime import datetime

base_url = "https://www.blogdumoderateur.com/articles/"
articles = []
page = 1
DELAY = 1.5  # secondes entre chaque requête
TARGET = 200  # nombre d'articles visés 

while len(articles) < TARGET:
    url = base_url if page == 1 else f"{base_url}page/{page}/"
    print(f"Lecture : {url}")

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()

    except Timeout:
        print(f"Timeout sur {url}, on arrête la pagination.")
        break

    except HTTPError as e:
        print(f"Erreur HTTP {e.response.status_code} sur {url}, on arrête la pagination.")
        break

    soup = BeautifulSoup(r.text, "html.parser")
    posts = soup.select("article")

    if not posts:
        print("Aucun article trouvé sur cette page, fin de pagination.")
        break

    for post in posts:
        t = post.select_one("header.entry-header h3.entry-title")
        l = post.select_one("header.entry-header a")
        c = post.select_one(".favtag")
        ch = post.select_one(".entry-excerpt")
        d = post.select_one("time.entry-date")
    
        titre = t.get_text(strip=True) if t else None
        lien = l["href"] if l else None
        date = d["datetime"] if d else None
        categorie = c.get_text(strip=True) if c else None
        chapo = ch.get_text(" ", strip=True) if ch else None
        
        date = datetime.fromisoformat(date).strftime("%d/%m/%Y")

        articles.append({
            "titre": titre,
            "url": lien,
            "categorie": categorie,
            "chapo": chapo,
            "date": date,
        }) 
        if len(articles) >= 200:
            break
    page += 1
    time.sleep(DELAY)  # délai entre requêtes
df = pd.DataFrame(articles)
df.to_csv("articles.csv", index=False, encoding="utf-8-sig")
print(f"Export terminé : {len(df)} lignes")