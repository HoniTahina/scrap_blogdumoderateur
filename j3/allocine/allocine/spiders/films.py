import re
import scrapy
from allocine.items import FilmItem


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/meilleurs/"]

    custom_settings = {
        "USER_AGENT": "IPSSI-scraper (+contact@ipssi.fr)",
        "DOWNLOAD_DELAY": 1,
    }

    films_collectes = 0
    limite = 50

    def parse(self, response):
        cartes = response.css("li.mdl")

        for carte in cartes:
            if self.films_collectes >= self.limite:
                return

            titre = carte.css(".meta-title-link::text").get()
            url_relative = carte.css(".meta-title-link::attr(href)").get()
            realisateur = None
            bloc_real = carte.css(".meta-body-direction")
            if bloc_real:
                textes = bloc_real.css("::text").getall()
                textes = [t.strip() for t in textes if t.strip() and t.strip().lower() != "de"]
                if textes:
                    realisateur = " ".join(textes)

            if not titre or not url_relative:
                continue

            note_presse = None
            note_spectateurs = None
            for item_note in carte.css(".rating-item"):
                label = " ".join(item_note.css(".rating-title::text").getall()).strip().lower()
                note = item_note.css(".stareval-note::text").get()
                if "presse" in label:
                    note_presse = note.strip() if note else None
                elif "spectateurs" in label:
                    note_spectateurs = note.strip() if note else None

            url_absolue = response.urljoin(url_relative)
            self.films_collectes += 1

            item = FilmItem(
                titre=titre.strip(),
                realisateur=realisateur.strip() if realisateur else None,
                note_presse=note_presse,
                note_spectateurs=note_spectateurs,
                url=url_absolue,
            )

            yield response.follow(
                url_absolue,
                callback=self.parse_fiche,
                cb_kwargs={"item": item},
            )

        if self.films_collectes < self.limite:
            match = re.search(r"page=(\d+)", response.url)
            num_page = int(match.group(1)) + 1 if match else 2
            url_suivante = f"https://www.allocine.fr/film/meilleurs/?page={num_page}"
            yield response.follow(url_suivante, callback=self.parse)

    def parse_fiche(self, response, item):
        annee = None
        for bloc in response.css(".item"):
            label = bloc.css(".what::text").get() or ""
            if "année de production" in label.strip().lower():
                annee = bloc.css(".that::text").get()
                if annee:
                    annee = annee.strip()
                break

        item["annee"] = annee
        yield item