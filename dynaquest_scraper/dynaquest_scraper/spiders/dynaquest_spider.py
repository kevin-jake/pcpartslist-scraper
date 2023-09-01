import scrapy
from dynaquest_scraper.items import GPUProduct
import time
import random


class DynaquestSpiderSpider(scrapy.Spider):
    name = "dynaquest_spider"
    allowed_domains = ["dynaquestpc.com"]
    start_urls = ["https://dynaquestpc.com/collections/graphics-card"]


    async def parse(self, response):
        last_page_number = response.css('li.ellipsis.disabled + li a::text').get()
        print("--------------------------------")
        print(last_page_number)
        print("--------------------------------")

        for page in range(int(last_page_number)):
            if page:
                full_url = "https://dynaquestpc.com/collections/graphics-card?page=" + str(page)
                time.sleep(random.randint(1,2))
                print('-------------------------')
                print(full_url)
                print('-------------------------')
                yield scrapy.Request(url=full_url, callback=self.parse_page)
        pass

    async def parse_page(self, response):
        get_hrefs = response.css('div.product-title a::attr(href)')
        for url in get_hrefs:
            full_url = "https://dynaquestpc.com" + url.get()
            time.sleep(random.randint(1,2))
            # print('-------------------------')
            # print(full_url)
            # print('-------------------------')
            yield scrapy.Request(url=full_url, callback=self.parse_product)


    async def parse_product(self, response):
        product_item = GPUProduct()
        promo = None
        raw_price = response.css("h2#price-preview.price ::text").get()
        price = raw_price.split('.')[0].replace('₱', '').replace(',','').strip()
        name = response.css("h1.title ::text").get()
        raw_orig_price =  response.css("del ::text").get()
        if raw_orig_price is not None:
            orig_price = raw_orig_price.split('.')[0].replace('₱', '').replace(',','')
            promo = str(round((( int(orig_price) - int(price)) / int(orig_price) )*100)) + "% off"

        product_item['url'] = response.url
        product_item['name'] = name
        product_item['price'] = price
        product_item['brand'] = name.split()[0]
        product_item['supplier'] = 'Dynaquest'
        product_item['promo'] = promo
        # TODO: Add stocks and warranty
        yield product_item