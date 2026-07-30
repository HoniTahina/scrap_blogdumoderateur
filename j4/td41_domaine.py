# td41_domaine.py
import requests, json, socket
import whois 
import time
import sys

HEADERS = {"User-Agent": "IPSSI-OSINT (+cours@ipssi.fr)"}
def analyse_whois(domaine: str) -> dict:
    try:
        w = whois.whois(domaine)
        return {
            "registrar" : str(w.registrar or "n/a"),
            "creation_date" : str(w.creation_date or "n/a")[:10],
            "expiration_date": str(w.expiration_date or "n/a")[:10],
            "name_servers" : list(set(w.name_servers or [])),
            "country" : str(w.country or "n/a"),
        }
    except Exception as e:
        return {"erreur": str(e)}
def analyse_headers(domaine: str) -> dict:
    try:
        r = requests.head(f"https://{domaine}", headers=HEADERS, timeout=10, allow_redirects=True)
        h = r.headers
        return {
            "status" : r.status_code,
            "server" : h.get("Server", "n/a"),
            "x_powered_by" : h.get("X-Powered-By", "n/a"),
            "x_frame_options": h.get("X-Frame-Options", "n/a"),
            "csp_present" : "Content-Security-Policy" in h,
            "hsts_present" : "Strict-Transport-Security" in h,
        }
    except Exception as e:
        return {"erreur": str(e)}

def sous_domaines_crtsh(domaine: str, tries: int = 3) -> list[str]:
    """Cherche les sous-domaines via l'API publique crt.sh"""
    url = f"https://crt.sh/?q=%.{domaine}&output=json"
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            data = r.json()
            subs = list(set(
                entry["name_value"]
                for entry in data
                if "*" not in entry["name_value"]
                and entry["name_value"].endswith(domaine)
            ))
            return sorted(subs)[:100]
        except Exception as e:
            print(f"  crt.sh tentative {attempt+1}/{tries} echouee : {e}")
            if attempt < tries - 1:
                time.sleep(2 ** attempt)  # backoff : 1s, 2s, 4s
    return [f"ERREUR apres {tries} tentatives"]

def analyse_robots(domaine: str) -> str:
    try:
        r = requests.get(f"https://{domaine}/robots.txt",
        headers=HEADERS, timeout=10)
        return r.text[:1000] if r.status_code == 200 else f"HTTP {r.status_code}"
    except Exception as e:
        return str(e)
def analyser_domaine(domaine: str) -> dict:
    print(f"[*] Analyse de {domaine}...")
    rapport = {
        "domaine" : domaine,
        "ip" : socket.gethostbyname(domaine) if domaine else "n/a",
        "whois" : analyse_whois(domaine),
        "headers_http" : analyse_headers(domaine),
        "sous_domaines": sous_domaines_crtsh(domaine),
        "robots_txt" : analyse_robots(domaine),
    }
    rapport["nb_sous_domaines"] = len(rapport["sous_domaines"])
    return rapport

if __name__ == "__main__":
    domaine = sys.argv[1] if len(sys.argv) > 1 else "wikipedia.org"
    time.sleep(1) # politesse
    rapport = analyser_domaine(domaine)
    sortie = f"rapport_{domaine}.json"
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)
    print(f"[+] Rapport sauvegarde : {sortie}")
    print(f" {rapport['nb_sous_domaines']} sous-domaines trouves")
    print(f" Serveur : {rapport['headers_http'].get('server','n/a')}")