import requests, time
import csv
import sqlite3
import argparse
from bs4 import BeautifulSoup
HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}
def get_page(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")
 
# def parse_articles(soup: BeautifulSoup) -> list[dict]:
#     articles = []
#     for card in soup.select("article"):
#         titre = card.select_one("header.entry-header h3.entry-title")
#         url = card.select_one("header.entry-header a")
#         date = card.select_one("time.entry-date")
#         categorie= card.select_one(".favtag")
#         chapeau = card.select_one(".entry-excerpt")

#         articles.append({
#             "titre": titre.get_text(strip=True) if titre else None,
#             "url": url["href"] if url else None,
#             "date": date["datetime"] if date else None,
#             "categorie": categorie.get_text(strip=True) if categorie else None,
#             "chapeau": chapeau.get_text(" ", strip=True) if chapeau else None
#         })
#     return articles

BASE_URL = "https://www.blogdumoderateur.com/articles/page/{n}/"
MAX = 200
def scrape_all(max_articles=MAX) -> list[dict]:
    tous = []
    page = 1
    while len(tous) < max_articles:
        url = "https://www.blogdumoderateur.com/articles/" if page == 1 else BASE_URL.format(n=page)
        soup = get_page(url)
        nouveaux = parse_articles(soup)
        if not nouveaux:
            print(f"Plus d'articles a la page {page}, arret.")
            break
        tous.extend(nouveaux)
        print(f"Page {page} => {len(nouveaux)} articles | total={len(tous)}")
        page += 1
        time.sleep(1.5)
    tous.sort(key=lambda a: a["date"], reverse=True)
    return tous[:max_articles]
def get_page(url: str, tries: int = 3) -> BeautifulSoup:
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"429 - attente {wait}s"); time.sleep(wait); continue
            r.raise_for_status()
            return BeautifulSoup(r.text, "lxml")
        except requests.Timeout:
            print(f"Timeout tentative {attempt+1}/{tries}")
            time.sleep(2 ** attempt)
        except requests.HTTPError as e:
            if e.response.status_code < 500:
                raise # 4xx definitif
        time.sleep(2 ** attempt)
    raise RuntimeError(f"Echec apres {tries} tentatives : {url}")

CHAMPS = ["titre", "url", "date", "categorie", "chapeau"]
def sauver_csv(articles: list[dict], chemin: str = "articles.csv") -> None:
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS, extrasaction="ignore")
        w.writeheader()
        w.writerows(articles)
        print(f"CSV : {len(articles)} lignes -> {chemin}")

DDL = '''
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    date TEXT,
    categorie TEXT,
    chapeau TEXT,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
)
'''
def sauver_sqlite(articles: list[dict], chemin: str = "articles.db") -> None:
    with sqlite3.connect(chemin) as cx:
        cx.execute(DDL)
        inserted = 0
        for a in articles:
            try:
                cx.execute(
                "INSERT OR IGNORE INTO articles (titre,url,date,categorie,chapeau) "
                "VALUES (:titre,:url,:date,:categorie,:chapeau)", a
                )
                inserted += cx.execute("SELECT changes()").fetchone()[0]
            except sqlite3.Error as e:
                print(f"Erreur SQLite : {e}")
            cx.commit()
        print(f"SQLite : {inserted} nouvelles lignes inserees dans {chemin}")

def main():
    p = argparse.ArgumentParser(description="Scraper Blog du Moderateur")
    p. add_argument("--max", type=int, default=200, help="Nb max d'articles")
    p.add_argument("--csv", default="articles.csv")
    p.add_argument("--db", default="articles.db")
    args = p.parse_args()
    print(f"Demarrage - cible : {args.max} articles")
    articles = scrape_all(args.max)
    sauver_csv(articles, args.csv)
    sauver_sqlite(articles, args.db)
    print(f"Termine : {len(articles)} articles")

def parse_articles(soup: BeautifulSoup) -> list[dict]:
    return [
        {
            "titre" : c.select_one("header.entry-header h3.entry-title").get_text(strip=True),
            "url" : (c.select_one("header.entry-header a") or {}).get("href",""),
            "date" : (c.select_one("time.entry-date[datetime]") or {}).get("datetime","")[:10],
            "categorie": el.get_text(strip=True) if (el := c.select_one(".favtag")) else "",
            "chapeau" : el.get_text(strip=True)[:300] if (el := c.select_one(".entry-excerpt")) else "",
        }
        for c in soup.select("article.post")
        if c.select_one("header.entry-header h3.entry-title")
    ]
if __name__ == "__main__":
 main()
