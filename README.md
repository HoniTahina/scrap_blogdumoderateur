url: https://www.blogdumoderateur.com/
Le scraping de la section /feed/ est-il autorise ? -> NON (https://www.blogdumoderateur.com/robots.txt)

Selecteur CSS:    
    titre: header.entry-header h3.entry-title
    url: header.entry-header a
    date: time.entry-date
    categorie: .favtag
    chapeau: .entry-excerpt (n'existe pas dans accueil mais dans https://www.blogdumoderateur.com/articles OUI)

Navigation vers la page 2 : https://www.blogdumoderateur.com/page/2/. 
    Confirmez que la structure HTML est identique. -> OUI
    Nombre d'articles par page = 41 dans accueil.
    Nombre d'articles par page = 15 dans articles.

NOTE: J'AI CHANGER L'URL PAR "https://www.blogdumoderateur.com/articles" PARCE QUE LES DONNEES SONT PLUS PROPRES

Pour creer venv:
    py -m venv .venv 
    .venv\Scripts\activate
    pip install -r requirements.txt