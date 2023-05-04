import scrapy
from scrapy_playwright.page import PageMethod
from pchub_scraper.items import GPUProduct

class PchubSpiderSpider(scrapy.Spider):
    name = "pchub_spider"
    allowed_domains = ["pchubonline.com"]
    start_urls = ["http://pchubonline.com/browse?product=all&br=true&ct=false&sort=default-asc&y[0]=GPU&y[1]=GPU"]

    
    def start_requests(self):
        url = "http://pchubonline.com/browse?product=all&br=true&ct=false&sort=default-asc&y[0]=GPU&y[1]=GPU"
        yield scrapy.Request(url, meta=dict(
            playwright = True,
            playwright_include_page = True,
            # playwright_page_methods = [
            #     PageMethods('wait_for_selector',)
            # ]
            errback = self.errback
        ))


    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_selector('#loadMoreBtn',timeout=10000)
        load_more_btn = await page.query_selector('#loadMoreBtn')
        await load_more_btn.click()

        while load_more_btn != None or '':
            try: 
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await page.wait_for_selector('#loadMoreBtn', timeout=10000)
                load_more_btn = await page.query_selector('#loadMoreBtn')
                await load_more_btn.click()
            except Exception as e:
                print(e)
                break
        scrolled  = scrapy.Selector(text=await page.content())
        await page.close()
        products = scrolled.xpath("//div[@class='flex flex-col p-3 gap-y-2 bg-white rounded-lg hover:cursor-pointer hover:shadow-lg']")
        for product in products:
            product_id = product.xpath('//div[@class="flex flex-row items-center justify-between"]/span[2]/text()').get()
            product_url = 'https://pchubonline.com/product' + product_id
            yield scrapy.Request(url=product_url, callback=self.parse_product)

    async def parse_product(self, response):
        product_item = GPUProduct()

        product_page = response.meta["playwright_page"]
        await product_page.wait_for_selector('span:contains("+")::text',timeout=1000)
        plus_btn = await product_page.query_selector('span:contains("+")::text')
        input_field = await product_page.query_selector('input[x-model="qty"]')
        input_field.fill("999")
        plus_btn.click()
        new_value = input_field.get_attribute("value")
        print(f"New value: {new_value}")
        await product_page.close()

        product_info = response.xpath('//div[@x-data="product_info($wire)"]/span')
        raw_name = product_info.css("span.my-1\.5.font-bold.capitalize").get()
        if len(raw_name.split(',')) == 0:
            name = raw_name.split('pn')[0].strip()
        else:
            if "[ Promo ]" in raw_name:
                name = raw_name.split('[ Promo ]')[1].strip()
            else:
                name = raw_name.strip()


        product_item['url'] = response.url
        product_item['name'] = name
        product_item['price'] = product_info.xpath(".//span/@x-text").get().split("(")[-1].split(")")[0].strip()
        product_item['brand'] = response.css("div.flex.flex-row.justify-between.md\:mx-5 > p ::text").get().split('>')[1].strip()
        product_item['supplier'] = 'PCHub'
        product_item['promo'] = product_info.css("span.text-red-500.text-sm ::text").get()
        product_item['warranty'] = product_info.css('span:contains("Warranty:")::text').get().split(":")[1]
        product_item['stocks'] = new_value
        yield product_item

    async def errback(self, error):
        page = error.request.nmeta("playwright_page")
        await page.close()