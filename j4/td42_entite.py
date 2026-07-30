# td42_entite.py
import requests, json, time
import feedparser
import sys
from bs4 import BeautifulSoup
HEADERS = {"User-Agent": "IPSSI-OSINT (+cours@ipssi.fr)"}
def chercher_sirene(nom: str) -> dict:
    """API officielle recherche-entreprises.api.gouv.fr -- pas besoin de cle API"""
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={nom}&page=1&per_page=1&sort_by_size=true"
    print(f"[debug] URL appelee : {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            ent = data["results"][0]
            siege = ent.get("siege", {}) or {}
            return {
                "siren": ent.get("siren"),
                "denomination": ent.get("nom_complet"),
                "adresse_siege": siege.get("adresse"),
                "code_naf": ent.get("activite_principale") or siege.get("activite_principale"),
                "date_creation": ent.get("date_creation") or siege.get("date_creation"),
                "tranche_effectif": ent.get("tranche_effectif_salarie") or siege.get("tranche_effectif_salarie"),
            }
        return {"resultat": "Non trouve dans SIRENE"}
    except Exception as e:
        return {"erreur": str(e)}

def scraper_wikipedia(nom: str) -> dict:
    """Scraper l'infobox et l'intro de la page Wikipedia"""
    slug = nom.replace(" ", "_")
    url = f"https://fr.wikipedia.org/wiki/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        infobox_table = soup.select_one("table.infobox, table.wikitable")

        infobox = {}
        if infobox_table:
            for tr in infobox_table.select("tr"):
                th = tr.select_one("th")
                td = tr.select_one("td")
                if th and td:
                    cle = th.get_text(strip=True)
                    val = td.get_text(" ", strip=True)[:200]
                    infobox[cle] = val

        # Premier paragraphe = introduction, en EXCLUANT les <p> qui sont
        # a l'interieur meme du tableau infobox (sinon on capte un bout
        # d'une cellule comme "Filiales" au lieu du vrai texte d'intro)
        intro = ""
        for p in soup.select("#mw-content-text p"):
            if infobox_table and infobox_table in p.parents:
                continue
            txt = p.get_text(strip=True)
            if len(txt) > 80:
                intro = txt[:500]
                break

        return {"infobox": infobox, "intro": intro, "url": url}
    except Exception as e:
        return {"erreur": str(e)}

def veille_presse(nom: str, nb_max: int = 10) -> list[dict]:
    """Google News RSS : articles recents mentionnant l'entite"""
    query = nom.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"
    feed = feedparser.parse(url)
    return [
        {
            "titre" : e.get("title",""),
            "source": e.get("source", {}).get("title",""),
            "date" : e.get("published",""),
            "lien" : e.get("link",""),
        }
        for e in feed.entries[:nb_max]
    ]

def construire_fiche(nom: str) -> dict:
    print(f"[*] Construction de la fiche pour : {nom}")
    fiche = {"entite": nom}
    fiche["sirene"] = chercher_sirene(nom); time.sleep(1)
    fiche["wikipedia"] = scraper_wikipedia(nom); time.sleep(1)
    fiche["presse"] = veille_presse(nom)
    fiche["nb_articles"] = len(fiche["presse"])
    return fiche

if __name__ == "__main__":
    nom = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "TotalEnergies"
    fiche = construire_fiche(nom)
    with open("fiche_entite.json","w",encoding="utf-8") as f:
        json.dump(fiche, f, indent=2, ensure_ascii=False)
    print(f"[+] Fiche sauvegardee : fiche_entite.json")
    print(f" SIREN : {fiche['sirene'].get('siren','n/a')}")
    print(f" Articles: {fiche['nb_articles']}")