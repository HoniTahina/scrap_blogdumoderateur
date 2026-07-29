## Analyse des performances de crawl (AlloCiné)

Test réalisé sur 50 films, en faisant varier le paramètre `CONCURRENT_REQUESTS`
(le nombre de requêtes que Scrapy peut envoyer en même temps).

### Commandes utilisées

\`\`\`powershell
Measure-Command { scrapy crawl films -s CONCURRENT_REQUESTS=1 *> run1.log }
Measure-Command { scrapy crawl films -s CONCURRENT_REQUESTS=4 *> run4.log }
Measure-Command { scrapy crawl films -s CONCURRENT_REQUESTS=8 *> run8.log }
Measure-Command { scrapy crawl films -s CONCURRENT_REQUESTS=16 *> run16.log }
\`\`\`

### Résultats mesurés

| CONCURRENT_REQUESTS | Temps total (s) | Films récupérés | Requêtes envoyées | Films/s |
|----------------------|------------------|-------------------|----------------------|---------|
| 1                    | 69.27            | 50                 | 56                    | 0.74    |
| 4                    | 68.49            | 50                 | 56                    | 0.75    |
| 8                    | 71.59            | 50                 | 56                    | 0.73    |
| 16                   | 69.75            | 50                 | 56                    | 0.74    |

### À partir de quelle valeur le gain devient négligeable ?

Résultat surprenant : dans mon cas, **il n'y a quasiment aucun gain**, même
entre 1 et 16 requêtes en parallèle. Les 4 temps sont pratiquement identiques
(entre 68 et 72 secondes), l'écart s'explique juste par la variabilité normale
du réseau, pas par le nombre de requêtes autorisées.

En creusant, la raison est probablement que mon `settings.py` fixe
`CONCURRENT_REQUESTS_PER_DOMAIN = 1`. Or toutes mes requêtes vont vers le même
site (allocine.fr) — donc c'est ce réglage-là qui limite vraiment la vitesse,
pas `CONCURRENT_REQUESTS` (qui ne compte que si on scrape plusieurs sites
différents en même temps). Changer `CONCURRENT_REQUESTS` sans toucher
`CONCURRENT_REQUESTS_PER_DOMAIN`, c'est un peu comme élargir une autoroute à 4
voies mais laisser un seul péage ouvert : ça ne change rien au trafic réel.

Le `DOWNLOAD_DELAY = 1` (1 seconde d'attente minimum entre deux requêtes vers
le même site) joue sûrement aussi un rôle : même avec plus de requêtes
"autorisées", chaque requête est de toute façon espacée d'au moins 1 seconde.

**Pour la suite**, un test plus parlant aurait été de faire varier
`CONCURRENT_REQUESTS_PER_DOMAIN` à la place, puisque c'est le vrai frein ici.

### Pourquoi AUTOTHROTTLE peut battre une valeur fixe élevée

Une valeur fixe (par exemple 16 requêtes en parallèle) reste la même tout le
temps, que le site réponde vite ou soit en train de ramer. Si le site est
lent ou surchargé, continuer à envoyer plein de requêtes d'un coup peut le
faire planter encore plus (erreurs, timeouts), ce qui au final ralentit tout
le crawl à cause des tentatives ratées.

`AUTOTHROTTLE` s'adapte en temps réel : il regarde combien de temps le site
met à répondre, et ajuste automatiquement la vitesse d'envoi. Résultat : il va
plus vite quand c'est possible, et ralentit tout seul quand il le faut,
plutôt que de suivre un chiffre fixe choisi à l'avance sans savoir si c'est
adapté au moment présent.

### Que veut dire un ratio "films récupérés / requêtes envoyées" trop bas

Dans mes tests : 50 films récupérés pour 56 requêtes envoyées, donc un ratio
d'environ 0.89 (89%). C'est logique : mon spider fait une requête pour la
page de liste (avec pagination) + une requête par fiche film pour aller
chercher l'année. Avec 50 films et 5-6 pages de liste visitées, ça fait bien
environ 56 requêtes pour 50 films récupérés.

**Un ratio en dessous de 0.5** voudrait dire qu'il faut presque 2 requêtes
pour obtenir 1 seul film — ce qui serait suspect et indiquerait un problème :
- des pages visitées qui ne donnent jamais de résultat (erreur de sélecteur
  sur certaines fiches, page en erreur 404, etc.),
- des liens suivis en double par erreur,
- de la pagination qui continue inutilement après avoir déjà assez de films.

Chez moi le ratio est proche de 0.9, donc c'est normal : presque chaque
requête sert bien à quelque chose, à part le petit coût des pages de liste qui
ne donnent pas de film directement mais juste des liens à suivre.