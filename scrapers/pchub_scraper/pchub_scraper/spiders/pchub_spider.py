import scrapy
from pchub_scraper.items import Product
import time
import random
import yaml
from datetime import datetime
import os 
class PchubSpiderSpider(scrapy.Spider):
    name = "pchub_spider"
    allowed_domains = ["pchubonline.com"]
    start_urls = ["https://pchubonline.com"]

    
    def start_requests(self):
        with open(os.path.join(os.path.dirname(__file__),"../../../../config/pchub_scraper.yaml"), "r") as f:
            configuration = yaml.load(f, Loader=yaml.FullLoader)
            shop_config = configuration['pchub']
        url = "https://pchubonline.com/browse?product=all&br=true&ct=false&sort=default-asc&y[0]=" + shop_config['category'][self.product] + "&y[1]=" + shop_config['category'][self.product]
        yield scrapy.Request(url,
            meta=dict(
            playwright = True,
            config=shop_config,
            playwright_include_page = True,
            errback = self.errback
        ))


    async def parse(self, response):
        page = response.meta["playwright_page"]
        config = response.meta["config"]
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_selector('#loadMoreBtn',timeout=10000)
        load_more_btn = await page.query_selector('#loadMoreBtn')
        await load_more_btn.click()

        while load_more_btn != None or '':
            try: 
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await page.wait_for_selector('#loadMoreBtn', timeout=10000)
                load_more_btn = await page.query_selector('#loadMoreBtn')
                time.sleep(random.randint(0,3))
                await load_more_btn.click()
            except Exception as e:
                self.logger.error(e)
                break
        scrolled  = scrapy.Selector(text=await page.content())
        await page.close()
        products = scrolled.xpath("//div[@class='flex flex-col p-3 gap-y-2 bg-white rounded-lg hover:cursor-pointer hover:shadow-lg']")
        for product in products:
            product_id = product.xpath('.//div[@class="flex flex-row items-center justify-between"]/span[2]/text()').get()
            product_url = 'https://pchubonline.com/product/' + product_id
            time.sleep(random.randint(1,2))
            yield scrapy.Request(url=product_url, callback=self.parse_product, meta=dict(
            playwright = True,
            playwright_include_page = True,
            config=config,
            # playwright_page_methods = [
            #     PageMethods('wait_for_selector',)
            # ]
            errback = self.errback
            ))

    async def parse_product(self, response):
        product_item = Product()

        product_page = response.meta["playwright_page"]
        config = response.meta["config"]
        await product_page.wait_for_selector('div[x-data="product_info($wire)"] span',timeout=5000)
        sold_out = await product_page.query_selector('div.flex.flex-row.items-center span.text-red-500.font-medium')
        if sold_out is None:
            plus_btn = await product_page.query_selector('div.flex.flex-row.items-center:nth-of-type(n) button.bg-blue-primary.text-white.px-3.py-1.rounded.transition:nth-of-type(2)')
            input_field = await product_page.query_selector('input[x-model="qty"]')
            await input_field.fill("998")
            await plus_btn.click()
            while await product_page.query_selector('p.text-sm.text-red-600.ml-2') is None:
                await plus_btn.click()
                time.sleep(random.randint(0,3))
            new_value = await product_page.input_value('input[x-model="qty"]')
        else:
            new_value = 0
        await product_page.close()
        raw_id = response.url.split('/')[-1].strip()
        product_info = response.xpath('//div[@x-data="product_info($wire)"]/span')
        raw_name = product_info.css("span.my-1\.5.font-bold.capitalize ::text").get()
        raw_price = product_info.xpath("//span/@x-text").get()
        if len(raw_name.split(',')) == 0:
            name = raw_name.split('pn')[0].strip()
        else:
            if "[ Promo ]" in raw_name:
                name = raw_name.split('[ Promo ]')[1].split(',')[0].strip()
            if "[ Clearance! ]" in raw_name:
                name = raw_name.split('[ Clearance! ]')[1].split(',')[0].strip()
            else:
                name = raw_name.split(',')[0].strip()
        
        if raw_price is None:
            price = None
        else:
            price = raw_price.split("(")[-1].split(")")[0].strip()
        product_item['id'] = config['id_prefix'] + self.product + "-" + raw_id
        product_item['url'] = response.url
        product_item['name'] = name
        product_item['price'] = price
        product_item['product_type'] = self.product
        product_item['brand'] = response.css("div.flex.flex-row.justify-between.md\:mx-5 > p ::text").get().split('>')[1].strip()
        product_item['supplier'] = 'PCHub'
        product_item['promo'] = product_info.css("span.text-red-500.text-sm ::text").get()
        product_item['warranty'] = product_info.css('span:contains("Warranty:")::text').get().split(":")[1].strip()
        product_item['stocks'] = new_value
        product_item['image'] = 'https://assets.pchubonline.com/' + raw_id + '.jpg'
        product_item['date_scraped'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print('---------------------------------------------------------------------------------------------')
        # print(product_item)
        # print('---------------------------------------------------------------------------------------------')
        yield product_item

    async def errback(self, error):
        page = error.request.nmeta("playwright_page")
        await page.close()