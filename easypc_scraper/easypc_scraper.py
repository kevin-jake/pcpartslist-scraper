from shopify_scraper import scraper
import json

url = "https://easypc.com.ph/collections/graphic-card"
result = ['init']
page = 1
product_items = []

def parse_product(result):
    for item in result:
        product_item = {}
        print('----------------------------------------------------')
        print(item)
        print('----------------------------------------------------')
        product_item['url'] =  "https://easypc.com.ph/collections/graphic-card/products/" + item['handle']
        product_item['name'] = item['title']
        product_item['price'] = float(item['variants'][0]['price'])
        product_item['brand'] = item['vendor']
        product_item['supplier'] = 'EasyPC'
        promo_price = item['variants'][0]['compare_at_price']
        if promo_price:
            product_item['promo'] = 'Save ' + str(float(promo_price) - product_item['price'])
        # product_item['warranty'] = response.css('div.MuiBox-root.css-i2n2aa div.MuiBox-root.css-w55c3f p::text').get().strip()
        # product_item['stocks'] = item['stocks_left']
        # TODO: Find way to scrape inventory number in shopify
        print('----------------------------------------------------')
        print(product_item)
        print('----------------------------------------------------')
        product_items.append(product_item)
    return product_items

while len(result) != 0:
    data = scraper.get_json(url,page)
    result = json.loads(data)['products']
    parse_product(result)
    page += 1

jsonString = json.dumps(product_items)
jsonFile = open("easypc.json", "w")
jsonFile.write(jsonString)
jsonFile.close()

