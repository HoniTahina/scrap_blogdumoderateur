# items.py
import scrapy

class FilmItem(scrapy.Item):
    titre = scrapy.Field()
    annee = scrapy.Field()
    realisateur = scrapy.Field()
    note_presse = scrapy.Field()
    note_spectateurs = scrapy.Field()
    url = scrapy.Field()