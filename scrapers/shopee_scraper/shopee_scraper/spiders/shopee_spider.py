import scrapy
from shopee_scraper.items import GPUProduct
import time
import random
import yaml
from datetime import datetime
import os



class ShopeeScraperSpider(scrapy.Spider):
    name = "shopee_spider"
    allowed_domains = ["shopee.ph"]
    start_urls = ["http://shopee.ph/"]


    def start_requests(self):
        with open(os.path.join(os.path.dirname(__file__),"../../../../config/shopee_scraper.yaml"), "r") as f:
            configuration = yaml.load(f, Loader=yaml.FullLoader)
            shop_config = configuration['shops'][self.shop]
            selectors = configuration['selectors']
        url = "https://shopee.ph/search?facet=" + configuration['facets'][self.product] + "&noCorrection=true&page=0&searchKeyword=" + shop_config['searchKeyword'] + "&shop=" + shop_config['shop_id'] 
        print('---------------------------------------------------------------------------------------------')
        print(url)
        print('---------------------------------------------------------------------------------------------')

        yield scrapy.Request(url,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                configuration={'selectors': selectors, 'shop_config': shop_config, 'configuration': configuration},
                errback=self.errback
            ))


    async def parse(self, response):
        page = response.meta["playwright_page"]
        config = response.meta["configuration"]
        configuration = config['configuration']
        selectors = config['selectors']
        shop_config = config['shop_config']

        await page.wait_for_selector(selectors['main'],timeout=10000)
        total_page = int(response.css(selectors['total_page']).get())
        await page.close()

        for page_number in range(0,total_page):
            if page_number != total_page:
                full_url = "https://shopee.ph/search?facet=" + configuration['facets'][self.product] + "&noCorrection=true&page=" + str(page_number) + "&searchKeyword=" + shop_config['searchKeyword'] + "&shop=" + shop_config['shop_id']
                time.sleep(random.randint(1,2))
                yield scrapy.Request(url=full_url, callback=self.parse_page, dont_filter=True, meta=dict(
                playwright = True,
                playwright_include_page = True,
                selectors=selectors,
                shop_config=shop_config,
                errback = self.errback
                ))

    async def parse_page(self, response):
        product_page = response.meta["playwright_page"]
        selectors = response.meta['selectors']
        shop_config = response.meta['shop_config']

        await product_page.wait_for_selector(selectors['main'],timeout=10000)
        fullpage  = scrapy.Selector(text=await product_page.content())
        await product_page.close()
        get_hrefs = fullpage.css(selectors['get_hrefs'])
        for slug in get_hrefs:
            url = slug.css('a::attr(href)').get()
            # print('---------------------------------------------------------------------------------------------')
            # print(url)
            # print('---------------------------------------------------------------------------------------------')
            full_url = "http://shopee.ph" + url
            # print('---------------------------------------------------------------------------------------------')
            # print(full_url)
            # print('---------------------------------------------------------------------------------------------')
            time.sleep(random.randint(1,2))
            yield scrapy.Request(url=full_url, callback=self.parse_product, meta=dict(shop_config=shop_config,selectors=selectors))

    async def parse_product(self, response):
        shop_config = response.meta['shop_config']
        product_selectors = response.meta['selectors']['product']
        product_item = GPUProduct()
        # promo = None

        name = response.css(product_selectors['name']).get()
        raw_price = response.css(product_selectors['price']).get()
        price = raw_price.split('.')[0].replace('₱', '').replace(',','').strip()
        raw_id = response.url.split('.')[-1].split('?')[0]

        product_item['id'] = shop_config['id_prefix'] + self.product + "-" + raw_id
        product_item['url'] = response.url
        product_item['name'] = name
        product_item['price'] = price
        product_item['brand'] = response.css(product_selectors['brand']).get()
        product_item['stocks'] = response.css(product_selectors['stock']).get()
        product_item['vendor'] = shop_config['vendor']
        product_item['category_id'] = self.product
        product_item['image'] = response.css(product_selectors['image']).get()
        product_item['createdAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        product_item['promo'] = None
        product_item['warranty'] = None
        yield product_item


    async def errback(self, error):
        page = error.request.nmeta("playwright_page")
        await page.close()