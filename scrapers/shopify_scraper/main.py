import json
import requests
# import argparse
from datetime import datetime
from config import shopify_scraper_config
import scrapers.modules.save_to_db as database



# parser = argparse.ArgumentParser(
#     description= "This is used for generic shopify sites scraping"
# )

# parser.add_argument('-s', '--site', metavar='site', required=True, help='indicate the website you want to scrape')
# parser.add_argument('-p', '--product', metavar='product', required=True, help='the product on the website you want to scrape')

# args = parser.parse_args()


def get_json(url, page):
    """
    Get Shopify products.json from a store URL.

    Args:
        url (str): URL of the store.
        page (int): Page number of the products.json.
    Returns:
        products_json: Products.json from the store.
    """

    try:
        response = requests.get(f'{url}/products.json?limit=250&page={page}', timeout=5)
        products_json = response.text
        response.raise_for_status()
        return products_json

    except requests.exceptions.HTTPError as error_http:
        print("HTTP Error:", error_http)

    except requests.exceptions.ConnectionError as error_connection:
        print("Connection Error:", error_connection)

    except requests.exceptions.Timeout as error_timeout:
        print("Timeout Error:", error_timeout)

    except requests.exceptions.RequestException as error:
        print("Error: ", error)


def parse_product(url, product, item, config):
    product_item = {}
    print('----------------------------------------------------')
    print(item)
    print('----------------------------------------------------')
    if item['variants'][0]['id']:
        product_item['id'] =  config['id_prefix'] + product + "-" + str(item['id'])
        product_item['url'] =  url + "/products/" + item['handle']
        product_item['name'] = item['title']
        product_item['price'] = item['variants'][0]['price']
        product_item['brand'] = item['vendor']
        product_item['vendor'] = config['vendor']
        product_item['category_id'] = product
        product_item['description'] = str(item['body_html']).replace("\n", "")
        # TODO: Fix image loading on datablitz sites and make images an array of images.
        if len(item['images']) > 0:
            product_item['image'] = item['images'][0]['src']
        else:
            product_item['image'] = None
        product_item['createdAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        promo_price = item['variants'][0]['compare_at_price']


        if promo_price:
            compare_price = float(promo_price) - float(product_item['price'])
            if compare_price > 0:
                product_item['promo'] = 'Save ' + str(compare_price)
            else:
                product_item['promo'] = None
        else:
            product_item['promo'] = None
        # TODO: Find way to scrape inventory number in shopify
        # product_item['warranty'] = response.css('div.MuiBox-root.css-i2n2aa div.MuiBox-root.css-w55c3f p::text').get().strip()
        # product_item['stocks'] = item['stocks_left']
        product_item['warranty'] = None
        product_item['stocks'] = None
        # print('----------------------------------------------------')
        # print(product_item)
        # print('----------------------------------------------------')
    return product_item

 

# if __name__ == "__main__":
def main(site, product, test_limit, db_save=0):
    product_items = []
    config = shopify_scraper_config[site]
    result = ['init']
    page = 1
    url = config['site_url'] + '/collections/' + config['slug'][product]
    while len(result) != 0:
        try:
            data = get_json(url,page)
        except Exception as e:
            print(e)
            pass
        if data:
            result = json.loads(data)['products']
            for item in result:
                if site == 'datablitz':
                    tags = config['tags']
                    if item['variants'][0]['available'] and tags[product] in item['tags']:
                        product_items.append(parse_product(url, product, item, config))
                else:
                    product_items.append(parse_product(url, product, item, config))
                if len(product_items) == test_limit and test_limit != 0:
                    break
        page += 1
        if len(product_items) == test_limit and test_limit != 0:
            break
    if db_save == 1: database.insertToDatabase(product_items)
    return product_items

    # jsonString = json.dumps(product_items, indent=2, separators=(',', ': '), ensure_ascii=False)
    # jsonFile = open(f'{config["filename_prefix"]}_{product}.json', "w")
    # jsonFile.write(jsonString)
    # jsonFile.close()