import scrapy
from scrapy_playwright.page import PageMethod
from easypc_scraper.items import GPUProduct
import time
import random



class PcworthSpiderSpider(scrapy.Spider):
    name = "easypc_spider"
    allowed_domains = ["easypc.com.ph"]
    start_urls = ["https://easypc.com.ph/collections/graphic-card"]

    def start_requests(self):
        url = "https://easypc.com.ph/collections/graphic-card"
        yield scrapy.Request(url,
            meta={
                "playwright": True,
                "wait_until": "load",
                "playwright_include_page": True,
                "errback": self.errback,
            })

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.wait_for_selector('div.snize-pagination li:nth-last-child(2)')
        fullpage  = scrapy.Selector(text=await page.content())
        await page.close()

        last_page_number = fullpage.css('div.snize-pagination li:nth-last-child(2)').css('a::attr(rev)').get()
        print("--------------------------------")
        print(last_page_number)
        print("--------------------------------")

        for page in range(2):
            if page:
                full_url = "https://easypc.com.ph/collections/graphic-card?page=" + str(page)
                time.sleep(random.randint(1,2))
                print('-------------------------')
                print(full_url)
                print('-------------------------')
                yield scrapy.Request(url=full_url, callback=self.parse_page, meta=dict(
                    playwright = True,
                    playwright_include_page = True,
                    wait_until="load",
                    errback = self.errback
                    ))


    async def parse_page(self, response):
        product_page = response.meta["playwright_page"]
        await product_page.wait_for_selector('div.snize-item')
        get_hrefs = response.css('li.snize-product a.snize-view-link')
        for href in get_hrefs:
            url = href.attrib['href']
            full_url = "https://easypc.com.ph" + url
            time.sleep(random.randint(1,2))
            print('-------------------------')
            print(full_url)
            print('-------------------------')
            yield scrapy.Request(url=full_url, callback=self.parse_product, meta=dict(
            playwright = True,
            playwright_include_page = True,
            wait_until="load",
            errback = self.errback
            ))

    async def parse_product(self, response):
        product_item = GPUProduct()
# TODO: Extrat the product item details using full_url = "https://easypc.com.ph" + url + ".json"
        page = response.meta["playwright_page"]
        await page.wait_for_selector('div.product-info')


        promo = response.xpath('//p[contains(@style, "color: hsl(0, 75%, 60%)")]').xpath('normalize-space(.)').get()
        print('-------------------------')
        print(promo)
        print('-------------------------')
        price = response.xpath('//div[@class="detail-price" and @itemprop="price"]').xpath('@content').get()
        name = response.xpath('//h1[@itemprop="name"]').xpath('@content').get()
        raw_orig_price = response.xpath('//del[@class="price-compare"]').xpath('.//span[@class="hidePrice"]/text()').get()
        if raw_orig_price is not None:
            orig_price = raw_orig_price.split('.')[0].replace('₱', '').replace(',','')
            promo = promo + "," + str(round((( int(orig_price) - int(price)) / int(orig_price) )*100)) + "% off"

        product_item['url'] = response.url
        product_item['name'] = name
        product_item['price'] = price
        product_item['brand'] = response.xpath('//div[@class="product-vendor"]').xpath('@title').get()
        product_item['supplier'] = 'EasyPC'
        product_item['promo'] = promo
        yield product_item

    async def errback(self, error):
        page = error.request.meta.get("playwright_page")
        if page:
            await page.close()