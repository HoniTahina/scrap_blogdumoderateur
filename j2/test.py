from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os, time, json

url = "https://www.doctolib.fr"
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)
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

def extraire_medecins(driver) -> list[dict]:
    cartes = driver.find_elements(By.CSS_SELECTOR, "div[class='dl-card-content']")
    resultats = []
    for carte in cartes[:10]: # limiter a 10
        try:
            nom = carte.find_element(By.CSS_SELECTOR, "h2[class*='dl-text-body']").text.strip()
            adr = carte.find_element(By.CSS_SELECTOR, "p[class*='text-bf-UcI']").text.strip()
            url_el = carte.find_element(By.CSS_SELECTOR, "a[href*='/praticien/']")
            url = url_el.get_attribute("href")
            creneaux = [
                el.text.strip()
                for el in carte.find_elements(By.CSS_SELECTOR, "[class*='slot']")[:3]
            ]
            types = [
                el.text.strip()
                for el in carte.find_elements(By.CSS_SELECTOR, "[class*='consultation-mode']")
            ]
            resultats.append({
                "nom_specialite": nom, "adresse": adr,
                "type_consultation": types or ["n/a"],
                "prochains_creneaux": creneaux,
                "url_fiche": url,
            })
        except Exception as e:
            print(f"Carte ignoree : {e}")
    return resultats
medecins = extraire_medecins(driver)
driver.quit()
with open("doctolib.json","w",encoding="utf-8") as f:
    json.dump(medecins, f, indent=2, ensure_ascii=False)
print(f"{len(medecins)} medecins exportes dans doctolib.json")

