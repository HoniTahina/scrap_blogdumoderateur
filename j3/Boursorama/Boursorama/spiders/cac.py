import scrapy


class CacSpider(scrapy.Spider):
    name = "cac"
    allowed_domains = ["www.boursorama.com"]
    start_urls = ["https://www.boursorama.com"]

    def parse(self, response):
        pass
