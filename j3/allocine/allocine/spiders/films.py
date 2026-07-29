import scrapy


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr"]

    def parse(self, response):
        pass
