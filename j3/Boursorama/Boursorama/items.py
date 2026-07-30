# boursorama/items.py
import scrapy
class ActionItem(scrapy.Item):
 libelle = scrapy.Field()
 cours = scrapy.Field() # float
 variation = scrapy.Field() # float (ex: -0.53 pour -0.53%)
 volume = scrapy.Field() # int
 isin = scrapy.Field() # cle UNIQUE en BDD