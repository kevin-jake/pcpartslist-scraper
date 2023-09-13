from playwright.sync_api import sync_playwright
import json
import requests
import re
import yaml
import argparse
from datetime import datetime
import uuid


parser = argparse.ArgumentParser(
    description= "This is used for generic API sites scraping"
)

parser.add_argument('-s', '--site', metavar='site', required=True, help='indicate the website you want to scrape')
parser.add_argument('-p', '--product', metavar='product', required=True, help='the product on the website you want to scrape')

args = parser.parse_args()
auth_token = ''


with open("../config/api_scraper.yaml", "r") as f:
    configuration = yaml.load(f, Loader=yaml.FullLoader)
    config = configuration[args.site]

def pcworth_scraper(category):
    target_url = "https://www.pcworth.com/product/search/%20?limit=999&category=" + config[category]
    # Create a Playwright context (Chromium browser)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Enable network interception
        page.on(
        "request", lambda request: intercept_request(request)
    )

        product_items = []
        
        def intercept_request(request):
            global auth_token
            if request.url == "https://www.api.pcworth.com/api/ecomm/category/get":
                if request.headers['authorization']  != 'Bearer null' or  request.headers['authorization'] != '':
                    auth_token = request.headers['authorization']
        print(auth_token)

        # Open the target URL
        page.goto(target_url)

        # Wait for some time or perform other actions as needed
        # For example, you can wait for specific elements to load
        page.wait_for_selector('div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-6.MuiGrid-grid-sm-3.css-657qkj')

        # Close the browser
        browser.close()



    headers = {'Authorization': auth_token}
    print(headers)
    response = requests.get("https://www.api.pcworth.com/api/ecomm/products/available/get?limit=999&category=" + config[category], headers=headers)
    res = response.json()
    for item in res['data']:
        product_item = {}
        brand = ''
        print('----------------------------------------------------')
        print(item)
        print('----------------------------------------------------')
        brand_picture =  item['mfr_logo'].split("/")[-1]
        result = re.search(r"(.+?)\.png", brand_picture)


        if result:
            brand = result.group(0).capitalize().replace('.png', '')
        else:
            brand = "No brand found"

        product_item['id'] =  config['id_prefix'] + category + "-" + str(uuid.uuid4())
        product_item['url'] =  "https://www.pcworth.com/product/" + item['slug']
        product_item['name'] = item['product_name']
        product_item['price'] = item['amount']
        product_item['brand'] = brand
        product_item['supplier'] = 'PCWorth'
        product_item['promo'] = item['with_bundle']
        product_item['image'] = item['img_thumbnail']
        product_item['date_scraped'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        product_item['stocks'] = item['stocks_left']
        print('----------------------------------------------------')
        print(product_item)
        print('----------------------------------------------------')
        product_items.append(product_item)

    return product_items


if __name__ == "__main__":
    print (config)
    if args.site == 'pcworth':
        product_items = pcworth_scraper(args.product)
    jsonString = json.dumps(product_items, indent=2, separators=(',', ': '), ensure_ascii=False)
    jsonFile = open(f'{config["filename_prefix"]}_{args.product}.json', "w")
    jsonFile.write(jsonString)
    jsonFile.close()

