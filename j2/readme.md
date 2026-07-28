## Pourquoi Selenium plutôt que `requests` ?

Test réalisé pour vérifier si le contenu est rendu côté serveur ou côté client :

\`\`\`python
import requests
from bs4 import BeautifulSoup

r = requests.get("https://www.lesechos.fr",
    headers={"User-Agent": "IPSSI-scraper (+contact@ipssi.fr)"},
    timeout=10)
soup = BeautifulSoup(r.text, "lxml")
titres = soup.select("h2, h3")
print(f"{len(titres)} balises de titre trouvees")
\`\`\`

**Résultat : 0 balise de titre trouvée**, alors que la page affiche pourtant de
nombreux articles avec titres visibles dans le navigateur.

Ceci confirme que lesechos.fr est une application rendue côté client (React/Next.js) :
le HTML brut renvoyé par le serveur ne contient pas encore le contenu, qui est injecté
dynamiquement par JavaScript après chargement de la page. `requests` ne pouvant pas
exécuter de JavaScript, il est incapable de récupérer ce contenu.

**Selenium**, en pilotant un vrai navigateur Chrome, exécute le JavaScript comme le
ferait un utilisateur réel, ce qui permet de lire le DOM une fois le contenu chargé
(avec parfois un délai d'attente supplémentaire — `WebDriverWait` — pour les éléments
chargés de façon asynchrone, comme les créneaux de disponibilité sur Doctolib).

## Bonus - Comparaison headless vs normal

Mesure réalisée avec 3 essais par mode, sur la page d'accueil de lesechos.fr,
en attendant la présence du premier `<article>` :

\`\`\`python
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
\`\`\`

### Résultats (3 exécutions successives)

| Run | Normal | Headless | Gain |
|-----|--------|----------|------|
| 1   | 3.0s   | 2.5s     | 1.2x |
| 2   | 2.4s   | 2.5s     | 1.0x |
| 3   | 2.6s   | 2.4s     | 1.1x |

**Moyenne : Normal ≈ 2.7s / Headless ≈ 2.5s → gain d'environ 1.1x**

### Analyse

Contrairement au gain de 2-3x généralement attendu, le mode headless n'apporte ici
qu'un **gain marginal (~10%)**. Plusieurs explications possibles :

- Le temps mesuré est dominé par le **chargement réseau et l'exécution du JavaScript**
  de la page (requêtes API, hydratation React), pas par le rendu graphique lui-même.
  Le gain du mode headless vient surtout de l'absence de rendu GPU/compositing à
  l'écran, ce qui ne représente qu'une petite partie du temps total sur une page aussi
  lourde en JS.
- Sur une machine avec peu de charge graphique (pas de rendu 3D complexe), la
  différence entre affichage réel et headless est naturellement plus faible que sur
  des pages très riches visuellement.
- La variabilité réseau (latence vers lesechos.fr au moment du test) peut masquer une
  petite partie du gain réel : sur certains runs, le mode normal est même légèrement
  plus rapide que le headless, ce qui suggère que le bruit de mesure est du même ordre
  de grandeur que le gain lui-même.

### Conclusion

Sur ce cas précis, le mode headless reste préférable pour l'exécution automatisée
(pas de fenêtre à afficher, légèrement plus rapide, meilleure adaptation à un
environnement serveur/CI sans interface graphique), mais le gain de performance
mesuré est faible (~10%) plutôt que le x2-3 habituellement annoncé, probablement car
le goulot d'étranglement ici est le chargement réseau/JS et non le rendu visuel.