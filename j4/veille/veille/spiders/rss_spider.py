# veille/spiders/rss_spider.py
import scrapy
from veille.items import MentionItem
CIBLE = "canicule" # mot-cle a surveiller (modifiable)
MOTS_NEGATIFS = ["fraude","amende","condamne","scandale","plainte","liquidation","faillite","perquisition","accuse"]
MOTS_POSITIFS = ["croissance","benefice","record","acquisition","innovation","nomination","partenariat","expansion","investissement"]
FLUX_RSS = [
    "https://www.lemonde.fr/rss/une.xml",
    "https://www.lesechos.fr/rss/rss_une.xml",
    "https://www.lefigaro.fr/rss/figaro_actualites.xml",
    "https://www.bfmtv.com/rss/info/flux-rss/flux-toutes-les-actualites/",
    "https://www.01net.com/feed/",
]
class RssSpider(scrapy.Spider):
    name = "rss_spider"
    start_urls = FLUX_RSS
    custom_settings = {
        "ROBOTSTXT_OBEY" : True,
        "DOWNLOAD_DELAY" : 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "USER_AGENT" : "IPSSI-OSINT-veille (+cours@ipssi.fr)",
        "LOG_LEVEL" : "INFO",
    }
    def parse(self, response):
        articles = response.xpath("//item | //entry")
        self.logger.info(f"[DEBUG] {response.url} -> {len(articles)} articles trouves dans le flux")

        for item in articles:
            titre = item.xpath("title/text()").get("").strip()
            resume = item.xpath("description/text() | summary/text()").get("").strip()[:300]

            if CIBLE.lower() not in (titre + resume).lower():
                continue

            url = item.xpath("link/text() | link/@href").get("").strip()
            date_pub = item.xpath("pubDate/text() | published/text()").get("").strip()
            source = response.url.split("/")[2]

            texte = (titre + " " + resume).lower()
            neg = sum(1 for m in MOTS_NEGATIFS if m in texte)
            pos = sum(1 for m in MOTS_POSITIFS if m in texte)
            score = 1 if neg > pos else (2 if pos > neg else 0)

            yield MentionItem(
                titre=titre, url=url, source=source,
                date_publi=date_pub, resume=resume, score_alerte=score,
            )