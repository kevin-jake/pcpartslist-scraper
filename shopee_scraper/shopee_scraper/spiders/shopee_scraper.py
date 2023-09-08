import scrapy


class ShopeeScraperSpider(scrapy.Spider):
    name = "shopee_scraper"
    allowed_domains = ["shopee.ph"]
    start_urls = ["http://shopee.ph/"]

    def parse(self, response):
        pass
