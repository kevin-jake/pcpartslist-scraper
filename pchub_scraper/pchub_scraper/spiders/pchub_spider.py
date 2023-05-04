import scrapy
from scrapy_playwright.page import PageMethod

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
        await page.wait_for_selector('#loadMoreBtn',timeout=1000)
        load_more_btn = await page.query_selector('#loadMoreBtn')
        await load_more_btn.click()

        while load_more_btn != None or '':
            try: 
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await page.wait_for_selector('#loadMoreBtn', timeout=1000)
                load_more_btn = await page.query_selector('#loadMoreBtn')
                await load_more_btn.click()
                print('------------------------------------------------------------------')
                print(load_more_btn)
                print('------------------------------------------------------------------')
            except Exception as e:
                print('------------------------------------------------------------------')
                print("Done scrolling")
                print('------------------------------------------------------------------')
                break
        s  = scrapy.Selector(text=await page.content())
        await page.close()

        for product in s.xpath("//div[@class='flex flex-col p-3 gap-y-2 bg-white rounded-lg hover:cursor-pointer hover:shadow-lg']"):
            name = product.xpath(".//span[@class='font-bold text-xs lg:text-sm tracking-tight']/text()").get()
            price = product.xpath(".//div/@x-text").get()
            yield {
                'name': name.strip().split(',')[0] if name else None,
                'price': price.split("(")[-1].split(")")[0].strip() if price else None
            }

    async def errback(self, error):
        page = error.request.nmeta("playwright_page")
        await page.close()