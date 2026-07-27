import requests, time
import csv
import argparse
from bs4 import BeautifulSoup

from main import parse_articles

HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}   
BASE_URL = "https://quotes.toscrape.com/page/{n}/"
MAX = 20
CHAMPS = ["Citation", "Auteur", "Tag"]

def get_page(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def parse_citations(soup: BeautifulSoup) -> list[dict]:
    citations = []
    for card in soup.select("div.quote"):
        citation = card.select_one("span.text")
        auteur = card.select_one("small.author")
        tag = card.select_one("div.tags a.tag")

        citations.append({
            "Citation": citation.get_text(strip=True) if citation else None,
            "Auteur": auteur.get_text(strip=True) if auteur else None,
            "Tag": tag.get_text(strip=True) if tag else None
        })
    return citations
    
def scrape_all(max_citation=MAX) -> list[dict]:
    tous = []
    page = 1
    while len(tous) < max_citation:
        url = "https://quotes.toscrape.com/" if page == 1 else BASE_URL.format(n=page)
        soup = get_page(url)
        nouveaux = parse_citations(soup)
        if not nouveaux:
            print(f"Plus de citations à la page {page}, arrêt.")
            break
        tous.extend(nouveaux)
        print(f"Page {page} => {len(nouveaux)} citations | total={len(tous)}")
        page += 1
        time.sleep(1.5)
    return tous[:max_citation]

def sauver_csv(citations: list[dict], chemin: str = "citations_lemonde.csv") -> None:
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS, extrasaction="ignore")
        w.writeheader()
        w.writerows(citations)
        print(f"CSV : {len(citations)} lignes -> {chemin}")

def main():
    p = argparse.ArgumentParser(description="Scraper Le Monde - Planète")
    p.add_argument("--max", type=int, default=20, help="Nb max de citations")
    p.add_argument("--csv", default="citations_lemonde.csv")
    args = p.parse_args()
    print(f"Demarrage - cible : {args.max} articles")
    articles = scrape_all(args.max)
    sauver_csv(articles, args.csv)
    print(f"Termine : {len(articles)} articles")

if __name__ == "__main__":
 main()
