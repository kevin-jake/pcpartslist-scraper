from shopify_scraper import scraper
import json
import yaml
# import argparse
from datetime import datetime
import os, sys
sys.path.insert(0, os.path.abspath(".."))
# import modules.save_to_db as database



# parser = argparse.ArgumentParser(
#     description= "This is used for generic shopify sites scraping"
# )

# parser.add_argument('-s', '--site', metavar='site', required=True, help='indicate the website you want to scrape')
# parser.add_argument('-p', '--product', metavar='product', required=True, help='the product on the website you want to scrape')

# args = parser.parse_args()
product_items = []

def parse_product(url, product, result, config):
    for item in result:
        product_item = {}
        # print('----------------------------------------------------')
        # print(item)
        # print('----------------------------------------------------')
        if item['variants'][0]['available']:
            product_item['id'] =  config['id_prefix'] + product + "-" + str(item['id'])
            product_item['url'] =  url + "/products/" + item['handle']
            product_item['name'] = item['title']
            product_item['price'] = item['variants'][0]['price']
            product_item['brand'] = item['vendor']
            product_item['supplier'] = config['supplier']
            product_item['product_type'] = product
            if len(item['images']) > 0:
                product_item['image'] = item['images'][0]['src']
            product_item['date_scraped'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            promo_price = item['variants'][0]['compare_at_price']


            if promo_price:
                compare_price = float(promo_price) - float(product_item['price'])
                if compare_price > 0:
                    product_item['promo'] = 'Save ' + str(compare_price)
            else:
                product_item['promo'] = None
            # TODO: Find way to scrape inventory number in shopify
            # product_item['warranty'] = response.css('div.MuiBox-root.css-i2n2aa div.MuiBox-root.css-w55c3f p::text').get().strip()
            # product_item['stocks'] = item['stocks_left']
            product_item['warranty'] = None
            product_item['stocks'] = None
            print('----------------------------------------------------')
            print(product_item)
            print('----------------------------------------------------')
            product_items.append(product_item)
    return product_items

def parse_datablitz_product(url, product,result, config):
    for item in result:
        tags = config['tags']
        product_item = {}
        # print('----------------------------------------------------')
        # print(item)
        # print('----------------------------------------------------')
        if item['variants'][0]['available'] and tags[product] in item['tags']:
            product_item['id'] =  config['id_prefix'] + product + "-" + str(item['id'])
            product_item['url'] =  url + "/products/" + item['handle']
            product_item['name'] = item['title']
            product_item['brand'] = item['vendor']
            product_item['supplier'] = config['supplier']
            product_item['product_type'] = product
            promo_price = item['variants'][0]['compare_at_price']
            if promo_price:
                compare_price = float(promo_price) - float(product_item['price'])
                if compare_price > 0:
                    product_item['promo'] = 'Save ' + str(compare_price)
            else:
                product_item['promo'] = None
            if len(item['images']) > 0:
                product_item['image'] = item['images'][0]['src']
            product_item['date_scraped'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # TODO: Find way to scrape inventory number in shopify
            # product_item['warranty'] = response.css('div.MuiBox-root.css-i2n2aa div.MuiBox-root.css-w55c3f p::text').get().strip()
            # product_item['stocks'] = item['stocks_left']
            product_item['warranty'] = None
            product_item['stocks'] = None
            product_item['price'] = item['variants'][0]['price']

            print('----------------------------------------------------')
            print(product_item)
            print('----------------------------------------------------')
            product_items.append(product_item)
    return product_items

 

# if __name__ == "__main__":
def main(site, product):
    with open("../config/shopify_scraper.yaml", "r") as f:
        configuration = yaml.load(f, Loader=yaml.FullLoader)
        config = configuration[site]
    result = ['init']
    page = 1
    url = config['site_url'] + '/collections/' + config['slug'][product]
    while len(result) != 0:
        data = scraper.get_json(url,page)
        result = json.loads(data)['products']
        if site == 'datablitz':
            parse_datablitz_product(url, product, result, config)
        else:
            parse_product(url, product, result, config)
        page += 1
    return product_items

    # database.insertToDatabase(product_items)
    # jsonString = json.dumps(product_items, indent=2, separators=(',', ': '), ensure_ascii=False)
    # jsonFile = open(f'{config["filename_prefix"]}_{product}.json', "w")
    # jsonFile.write(jsonString)
    # jsonFile.close()