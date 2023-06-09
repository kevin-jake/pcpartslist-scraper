import scrapy
from scrapy_playwright.page import PageMethod
from pcworth_scraper.items import GPUProduct
import time
import random
import re

class PcworthSpiderSpider(scrapy.Spider):
    name = "pcworth_spider"
    allowed_domains = ["pcworth.com"]
    start_urls = ["https://www.pcworth.com/product/search/%20?limit=999&category=21&id=+"]

    def start_requests(self):
        url = "https://www.pcworth.com/product/search/%20?limit=999&category=21&id=+"
        yield scrapy.Request(url,
            meta=dict(
            playwright = True,
            wait_until="load",
            playwright_include_page = True,
            errback = self.errback
        ))


    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.wait_for_selector('div.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation1.MuiCard-root.css-iujtki')
        fullpage  = scrapy.Selector(text=await page.content())
        await page.close()
        
        product_urls = fullpage.css('div.MuiBox-root.css-1keu4rr  a::attr(href)')
        
        for product_url in product_urls:
            

            full_url = "https://www.pcworth.com" + product_url.get()
            time.sleep(random.randint(1,2))
            # print('-------------------------')
            # print(full_url)
            # print('-------------------------')
            yield scrapy.Request(url=full_url, callback=self.parse_product, meta=dict(
            playwright = True,
            playwright_include_page = True,
            wait_until="load",
            errback = self.errback
            ))
        

    async def parse_product(self, response):
        product_item = GPUProduct()
        brand = ''

        product_page = response.meta["playwright_page"]
        await product_page.wait_for_selector('div.MuiBox-root.css-1rre12o',timeout=5000)
        await product_page.wait_for_selector('h2.MuiBox-root.css-1uu0i36',timeout=5000)
        is_add_disabled = await product_page.query_selector('div.MuiBox-root.css-1rre12o button:nth-of-type(2)[disabled]')
        while is_add_disabled is None:
            plus_btn = await product_page.query_selector('div.MuiBox-root.css-1rre12o button:nth-of-type(2)')
            await plus_btn.click()
            time.sleep(random.randint(0,3))
            is_add_disabled = await product_page.query_selector('div.MuiBox-root.css-1rre12o button:nth-of-type(2)[disabled]')
        stocks = await product_page.inner_text('h3.MuiBox-root.css-pwppwr')
        await product_page.close()

        product_info = response.xpath('//div[@class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-6 css-bshnsv"]')
        raw_price = product_info.css("h2.MuiBox-root.css-1uu0i36 ::text").get()
        price = raw_price.split('.')[0].replace('₱', '').replace(',','')
        brand_picture = product_info.css("div.MuiBox-root.css-1coeexk img").xpath('@src').extract()
        brand_picture =  brand_picture[0].split("%2F")[-1]
        result = re.search(r"(.+?)\.png", brand_picture)


        if result:
            brand = result.group(0).capitalize().replace('.png', '')
        else:
            brand = "No brand found"

        product_item['url'] = response.url
        product_item['name'] = product_info.css("h1.MuiBox-root.css-1xi2frl ::text").get().strip()
        product_item['price'] = price
        product_item['brand'] = brand
        product_item['supplier'] = 'PCworth'
        product_item['promo'] = product_info.css("span.text-red-500.text-sm ::text").get()
        product_item['warranty'] = response.css('div.MuiBox-root.css-i2n2aa div.MuiBox-root.css-w55c3f p::text').get().strip()
        product_item['stocks'] = stocks
        yield product_item

    async def errback(self, error):
        page = error.request.nmeta("playwright_page")
        await page.close()

