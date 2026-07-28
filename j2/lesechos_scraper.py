# import requests
# from bs4 import BeautifulSoup
# r = requests.get("https://www.lesechos.fr",
#  headers={"User-Agent":"IPSSI-scraper (+contact@ipssi.fr)"},
#  timeout=10)
# soup = BeautifulSoup(r.text,"lxml")
# titres = soup.select("h2, h3")
# print(f"{len(titres)} balises de titre trouvees")
# Si 0 => page chargee en JS => Selenium necessaire

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, time

def make_driver(headless: bool = False):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opts)
# Mesurer le temps
import time
t0 = time.time()
driver = make_driver(headless=False)
driver.get("https://www.lesechos.fr")
WebDriverWait(driver,15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR,"article, [class*='article']"))
)
t_normal = time.time() - t0
print(f"Mode normal : {t_normal:.1f}s")

def extraire_articles(driver) -> list[dict]:
    articles = driver.find_elements(By.CSS_SELECTOR, "article")
    resultats = []
    for art in articles[:20]:
        try:
            lien_el = art.find_element(By.CSS_SELECTOR, "a[href]")
            url = lien_el.get_attribute("href")

            titre = ""
            try:
                titre = art.find_element(By.CSS_SELECTOR, "h3").text.strip()
            except: pass
            if not titre:
                titre = (lien_el.get_attribute("title") or lien_el.get_attribute("aria-label") or "").strip()
            if not titre: continue

            rubrique = ""
            try:
                rubrique = art.find_element(By.CSS_SELECTOR, "[data-testid='hubpage-links'] a").text.strip()
            except: pass

            chapeau = ""
            try:
                chapeau = art.find_element(By.CSS_SELECTOR, "[class*='sc-2xklta-4']").text.strip()[:300]
            except: pass

            heure = ""
            try:
                heure = art.find_element(By.CSS_SELECTOR, "time").text.strip()
            except: pass

            # Detecter le contenu premium (badge "Premium")
            premium = bool(art.find_elements(By.CSS_SELECTOR, "[data-testid='subscribe-badge']"))

            resultats.append({
                "titre": titre, "url": url, "rubrique": rubrique,
                "chapeau": chapeau, "heure_publi": heure, "premium": premium,
            })
        except Exception as e:
            pass
    return resultats


arts = extraire_articles(driver)
driver.quit()
with open("lesechos.json", "w", encoding="utf-8") as f:
    json.dump(arts, f, indent=2, ensure_ascii=False)
print(f"{len(arts)} articles exportes")

def mesurer_temps(headless, n_essais=3):
    temps = []
    for _ in range(n_essais):
        t0 = time.time()
        d = make_driver(headless=headless)
        d.get("https://www.lesechos.fr")
        WebDriverWait(d, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article")))
        temps.append(time.time() - t0)
        d.quit()
    return sum(temps) / len(temps)

t_normal = mesurer_temps(headless=False)
t_headless = mesurer_temps(headless=True)

print(f"Normal   (moyenne) : {t_normal:.1f}s")
print(f"Headless (moyenne) : {t_headless:.1f}s")
print(f"Gain               : {t_normal / t_headless:.1f}x plus rapide")