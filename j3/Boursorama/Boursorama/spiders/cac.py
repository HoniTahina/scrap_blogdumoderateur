# boursorama/spiders/cac.py
import re
import scrapy
from Boursorama.items import ActionItem


class CacSpider(scrapy.Spider):
    name = "cac"
    allowed_domains = ["boursorama.com"]
    start_urls = [
        "https://www.boursorama.com/bourse/actions/palmares/france/"
    ]

    def parse(self, response):
        for row in response.css("table.c-table tr.c-table__row"):
            cells = row.css("td.c-table__cell")
            if len(cells) < 7:
                continue

            lien = cells[0].css("a")
            href = lien.attrib.get("href", "")

            try:
                cours = float(cells[1].css("::text").get("0").replace(",", ".").strip())
                variation = float(cells[2].css("::text").get("0").replace(",", ".").replace("%", "").strip())
                volume = int(cells[6].css("::text").get("0").replace(" ", "").replace(",", "").strip() or 0)
            except (ValueError, TypeError):
                cours = variation = 0.0
                volume = 0

            item = ActionItem(
                libelle=lien.css("::text").get("").strip(),
                cours=cours,
                variation=variation,
                volume=volume,
            )

            url_absolue = response.urljoin(href)
            yield response.follow(
                url_absolue,
                callback=self.parse_fiche,
                cb_kwargs={"item": item},
            )

    def parse_fiche(self, response, item):
        isin_texte = response.css("h2.c-faceplate__isin::text").get()
        isin = None
        if isin_texte:
            match = re.search(r"[A-Z]{2}\d{10}", isin_texte)
            if match:
                isin = match.group(0)

        item["isin"] = isin
        yield item