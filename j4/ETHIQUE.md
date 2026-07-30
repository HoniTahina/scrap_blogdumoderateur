Quatre domaines DNS distincts gèrent la résolution du même nom
(`atos.net`), ce qui suggère une infrastructure **fragmentée entre
plusieurs entités/marques** plutôt qu'un DNS centralisé unique — cohérent
avec l'historique d'un grand groupe ayant traversé de nombreuses fusions et
acquisitions (chaque marque ayant conservé son infrastructure DNS d'origine
plutôt que d'être totalement unifiée sous un seul jeu de serveurs).

Un audit OSINT réel se heurte régulièrement à ce type d'aléa (disponibilité
des sources tierces) : c'est une contrainte à documenter plutôt qu'à
cacher.

---

# TD 4.2 : Cartographie de l'entité TotalEnergies

## 1. Ai-je le droit ?

Oui. Les trois sources utilisées sont conçues pour être consultées et
réutilisées publiquement :
- **API recherche-entreprises.api.gouv.fr** : API officielle de l'État
  français (DINUM/Etalab), qui synthétise le Registre National des
  Entreprises et la base SIRENE de l'INSEE — données publiques par
  construction légale.
- **Wikipédia** : contenu sous licence libre CC BY-SA, explicitement
  destiné à être consulté et réutilisé, y compris par des outils
  automatisés respectueux (User-Agent identifié, throttling).
- **Google News RSS** : flux RSS public, conçu par nature pour l'agrégation
  et la syndication de contenu.

Base légale RGPD : art. 6, intérêt légitime (veille concurrentielle/due
diligence documentée). Aucune authentification contournée.

## 2. Est-ce personnel ?

Globalement non, avec une nuance à noter : l'infobox Wikipédia contient un
nom de dirigeant (**Patrick Pouyanné, président-directeur général**). Il ne
s'agit pas d'une donnée personnelle sensible au sens du RGPD : c'est une
information publique liée à une **fonction professionnelle** au sein d'une
entreprise cotée, largement diffusée par l'entreprise elle-même et la
presse (obligation de transparence des sociétés cotées). Le reste des
données (SIREN, adresse du siège, code NAF, chiffre d'affaires, actualités
de presse) concerne la personne morale, pas des individus.

## 3. Suis-je discret ?

Non-dissimulation volontaire, comme pour le TD 4.1 :
- **User-Agent identifiable** : `"IPSSI-OSINT (+cours@ipssi.fr)"` sur
  chaque requête HTTP.
- **Throttling respecté** : `time.sleep(1)` entre chaque source interrogée.
- Les 3 sources sont interrogées à un rythme raisonnable, sans jamais
  automatiser de requêtes massives ou répétées vers une même cible.

## Bonus — Limite méthodologique observée (recherche par nom vs SIREN)

Une recherche par nom (`q=TotalEnergies`) sur l'API SIRENE fait remonter
**TOTALENERGIES MARKETING FRANCE** (SIREN 531680445), une filiale
commerciale, plutôt que la maison mère cotée **TotalEnergies SE** (SIREN
542051180, confirmé par l'infobox Wikipédia). Le paramètre
`sort_by_size=true` n'a pas corrigé ce biais (vérifié par un test dédié) :
le moteur de recherche textuel semble privilégier la correspondance de nom
la plus proche avant d'appliquer un quelconque tri par taille d'entité.

Ceci illustre une limite réelle de l'OSINT par recherche textuelle : un
grand groupe possède des centaines d'entités juridiques distinctes (903
filiales rien que pour TotalEnergies selon Wikipédia), et une requête par
simple nom de marque peut faire remonter la mauvaise entité juridique.

Pour une identification fiable en amont d'une acquisition ou d'un audit,
il serait indispensable de :
1. **Croiser plusieurs sources** pour confirmer l'identifiant exact de la
   cible (ici, Wikipédia a permis d'identifier le vrai SIREN de la maison
   mère, différent de celui remonté par la recherche textuelle),
2. **Privilégier une recherche par identifiant unique** (SIREN/SIRET) une
   fois celui-ci confirmé, plutôt que de se fier au premier résultat d'une
   recherche par nom.

Ce résultat a été conservé tel quel (sans forcer la correction vers la
maison mère) pour documenter honnêtement cette limite plutôt que de la
masquer — un comportement attendu d'un rapport OSINT professionnel, qui
doit toujours signaler ses angles morts et biais de collecte.

---

# TD 4.3 : Veille automatisée (flux RSS)

## 1. Ai-je le droit ?

Oui. Les flux RSS sont explicitement publiés par chaque média pour être
consultés et agrégés automatiquement — c'est la finalité même du format
RSS. `ROBOTSTXT_OBEY = True` est actif et respecté sur les 5 domaines
(5 requêtes robots.txt, 5 réponses 200 confirmées dans les logs).

## 2. Est-ce personnel ?

Non. La veille porte sur des entités/thématiques et leurs mentions dans la
presse généraliste — aucune collecte de données personnelles nominatives,
seulement du contenu éditorial déjà public.

## 3. Suis-je discret ?

Non-dissimulation volontaire : `USER_AGENT = "IPSSI-OSINT-veille
(+cours@ipssi.fr)"` explicite sur toutes les requêtes,
`DOWNLOAD_DELAY = 1.0` + `RANDOMIZE_DOWNLOAD_DELAY` respectés.

## Résultat et limite observée

Sur les 5 flux RSS ciblés, 1 a été bloqué (Les Échos, HTTP 403 — blocage
anti-scraping déjà rencontré ailleurs dans ce projet), et 4 ont répondu
normalement avec au total 93 articles récents (19 Figaro + 30 01net +
14 Le Monde + 30 BFMTV).

**Premier test avec `CIBLE = "TotalEnergies"`** : 0 correspondance trouvée
sur les 93 articles disponibles au moment du crawl (30/07/2026, 16h54).
Vérifié comme un vrai 0 et non une erreur technique, via un comptage debug
des articles bruts avant filtrage (qui confirme que le XPath extrait
correctement les items sur les 4 flux valides).

**Second test avec `CIBLE = "canicule"`** (sujet très présent dans
l'actualité du moment) : 5 correspondances trouvées sur le même ensemble
de flux, quasiment au même instant :

| Score | Titre | Source |
|---|---|---|
| 2 (positif) | "La chaleur estivale a un impact de plus en plus grave" | bfmtv.com |
| 0 (neutre) | Canicule : le gouvernement affirme avoir tenu sa promesse... | lemonde.fr |
| 0 (neutre) | Deux jours après le séisme au Japon, au moins 34 morts... | lemonde.fr |
| 0 (neutre) | DIRECT. Incendies en France: face à un feu "stabilisé"... | bfmtv.com |
| 0 (neutre) | Incendie en Gironde: des agriculteurs épandent de l'eau... | bfmtv.com |

**Anomalie de scoring à noter** : l'article "La chaleur estivale a un
impact de plus en plus grave" est scoré **positif (2)**, alors que son
contenu est manifestement alarmant. Ceci illustre une limite connue du
scoring par simple comptage de mots-clés : le classement ne tient pas
compte du sens réel de la phrase (le mot "grave" ne fait pas partie de la
liste `MOTS_NEGATIFS`, et un mot de la liste `MOTS_POSITIFS` a
probablement été détecté ailleurs dans le résumé sans rapport avec le ton
réel de l'article). Un système de scoring de sentiment fiable nécessiterait
une analyse sémantique (NLP) plutôt qu'un simple comptage lexical — ce que
ce TP ne prétend pas fournir, mais qu'il est important de signaler comme
limite dans un contexte professionnel où ce score pourrait à tort être
interprété comme fiable.

## Constat général

Cette comparaison (0 résultat avec TotalEnergies, 5 avec "canicule")
illustre une limite structurelle d'une veille par flux RSS générique : ces
flux ne contiennent que les tout derniers articles (quelques dizaines),
tous sujets confondus, donc la probabilité qu'une entité précise y
apparaisse à un instant T dépend entièrement de l'actualité du moment et de
la notoriété/fréquence de mention du sujet recherché.

Une veille professionnelle réelle tournerait en continu (cron toutes les
X minutes) pour accumuler les mentions sur la durée plutôt que sur un seul
instantané, ce qui réduirait la dépendance au hasard du moment précis de
l'exécution — ou utiliserait des flux déjà filtrés par mot-clé (comme le
flux Google News RSS du TD 4.2, qui cherche explicitement le terme et
retourne donc toujours des résultats si l'entité fait l'actualité
récemment), au prix d'une source unique plutôt que d'une vraie diversité
de médias.