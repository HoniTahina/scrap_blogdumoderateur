from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os, time, json
from selenium.common.exceptions import NoSuchElementException

url = "https://www.doctolib.fr"
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)
driver.get(url)

try:
    cookie_btn = wait.until(EC.element_to_be_clickable(
        (By.ID, "didomi-notice-agree-button"))
    )
    cookie_btn.click()
    print("Cookies accepted")
except Exception as e:
    print("No cookies button found")

try:
    search1 = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[placeholder='Nom, spécialité, établissement,...']")
        )
    )
    search1.clear()
    search1.send_keys("Chirurgien-dentiste")
    res = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button[id='1-Chirurgien-dentiste']")
        )
    )
    res.click()
except Exception as e:
    print("Error occurred while searching for dentist")
try:
    search2 = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[placeholder='Où ?']")
        )
    )
    search2.clear()
    search2.send_keys("Montpellier")
    res2 = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button[id='ChIJsZ3dJQevthIRAuiUKHRWh60']")
        )
    )
    res2.click()
except Exception as e:
    print("Error occurred while searching for location")

bouton = wait.until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button.searchbar-submit-button")
    )
)
bouton.click()

# Defiler pour charger les resultats hors viewport
def scroll_to_bottom(driver, pauses=3):
    last_h = driver.execute_script("return document.body.scrollHeight")
    for _ in range(pauses):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h
# Attendre que les cartes medecins soient visibles
try:
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div[class='dl-card-content']")
    ))
    print("Resultats charges")
    scroll_to_bottom(driver)
except Exception as e:
# Capture screenshot pour  debug
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot("screenshots/doctolib_erreur.png")
    raise RuntimeError(f"Resultats non charges : {e}")

def extraire_creneaux(carte) -> list:
    conteneurs = carte.find_elements(By.CSS_SELECTOR, "[data-test-id='availabilities-container']")
    if not conteneurs:
        return []

    pills = conteneurs[0].find_elements(By.CSS_SELECTOR, "[data-design-system-component='Pill']")
    creneaux = []
    for pill in pills:
        texte_complet = pill.get_attribute("textContent") or ""

        # on retire le texte cache (sr-only), ex: "Apres-midi", pour ne pas le coller au texte visible
        sr_textes = [
            sr.get_attribute("textContent").strip()
            for sr in pill.find_elements(By.CSS_SELECTOR, ".sr-only")
        ]
        texte_visible = texte_complet
        for sr in sr_textes:
            texte_visible = texte_visible.replace(sr, "")
        texte_visible = texte_visible.strip()

        if texte_visible:
            if sr_textes:
                creneaux.append(f"{texte_visible} ({sr_textes[0]})")
            else:
                creneaux.append(texte_visible)

    return creneaux[:3]


def extraire_medecins(driver) -> list[dict]:
    cartes = driver.find_elements(By.CSS_SELECTOR, "div.dl-card-content")
    resultats = []
    for i, carte in enumerate(cartes[:11]):
        try:
            nom = carte.find_element(By.CSS_SELECTOR, "h2").text.strip()
        except NoSuchElementException:
            # Pas un vrai medecin (carte sponsorisee, bandeau, etc.) -> on ignore silencieusement
            continue

        try:
            specialite = carte.find_element(By.CSS_SELECTOR, "p[class*='text-bf_UcI']").text.strip()
            nom_specialite = f"{nom} - {specialite}"

            adr = "n/a"
            icones_adresse = carte.find_elements(By.CSS_SELECTOR, "svg[aria-label='Adresse']")
            if icones_adresse:
                conteneur = icones_adresse[0].find_element(
                    By.XPATH, "./ancestor::div[contains(@class,'gap-8')][1]"
                )
                lignes = conteneur.find_elements(By.CSS_SELECTOR, "p")
                adr = ", ".join(l.text.strip() for l in lignes if l.text.strip())

            url_el = carte.find_element(By.CSS_SELECTOR, "a[href^='/']")
            url = url_el.get_attribute("href")

            creneaux = extraire_creneaux(carte)

            a_cabinet = len(carte.find_elements(By.CSS_SELECTOR, "svg[data-icon-name*='location-dot']")) > 0
            a_video = len(carte.find_elements(By.CSS_SELECTOR, "svg[data-icon-name*='video']")) > 0
            if a_cabinet and a_video:
                types = ["Cabinet", "Video"]
            elif a_video:
                types = ["Video"]
            elif a_cabinet:
                types = ["Cabinet"]
            else:
                types = ["n/a"]

            resultats.append({
                "nom_specialite": nom_specialite,
                "adresse": adr,
                "type_consultation": types,
                "prochains_creneaux": creneaux or ["n/a"],
                "url_fiche": url,
            })
        except Exception as e:
            print(f"Carte {i} ('{nom}') ignoree apres nom : {e.__class__.__name__}")

    return resultats
medecins = extraire_medecins(driver)
driver.quit()
with open("doctolib.json","w",encoding="utf-8") as f:
    json.dump(medecins, f, indent=2, ensure_ascii=False)
print(f"{len(medecins)} medecins exportes dans doctolib.json")

