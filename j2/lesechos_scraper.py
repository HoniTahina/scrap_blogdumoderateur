import requests
from bs4 import BeautifulSoup
r = requests.get("https://www.lesechos.fr",
 headers={"User-Agent":"IPSSI-scraper (+contact@ipssi.fr)"},
 timeout=10)
soup = BeautifulSoup(r.text,"lxml")
titres = soup.select("h2, h3")
print(f"{len(titres)} balises de titre trouvees")
# Si 0 => page chargee en JS => Selenium necessaire