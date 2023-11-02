from playwright.sync_api import sync_playwright
import requests
import re
import yaml
# import argparse
from datetime import datetime
import scrapers.modules.save_to_db as database


# parser = argparse.ArgumentParser(
#     description= "This is used for generic API sites scraping"
# )

# parser.add_argument('-s', '--site', metavar='site', required=True, help='indicate the website you want to scrape')
# parser.add_argument('-p', '--product', metavar='product', required=True, help='the product on the website you want to scrape')

# args = parser.parse_args()
auth_token = ''



def pcworth_scraper(category, config, test_limit):
    # print(category)
    target_url = "https://www.pcworth.com/product/search/%20?limit=999&category=" + config['category'][category]
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
        # print(auth_token)

        # Open the target URL
        page.goto(target_url)

        # Wait for some time or perform other actions as needed
        # For example, you can wait for specific elements to load
        page.wait_for_selector('div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-6.MuiGrid-grid-sm-3.css-657qkj')

        # Close the browser
        browser.close()



    headers = {'Authorization': auth_token}
    # print(headers)
    response = requests.get("https://www.api.pcworth.com/api/ecomm/products/available/get?limit=999&category=" + config['category'][category], headers=headers)
    res = response.json()
    for idx,item in enumerate(res['data']):
        product_item = {}
        brand = ''
        # print('----------------------------------------------------')
        # print(item)
        # print('----------------------------------------------------')
        brand_picture =  item['mfr_logo'].split("/")[-1]
        result = re.search(r"(.+?)\.png", brand_picture)


        if result:
            brand = result.group(0).capitalize().replace('.png', '')
        else:
            brand = "No brand found"

        product_item['id'] =  config['id_prefix'] + category + "-" + item['img_thumbnail'].split('/')[-1].strip('.jpg')
        product_item['url'] =  "https://www.pcworth.com/product/" + item['slug']
        product_item['name'] = item['product_name']
        product_item['price'] = item['amount']
        product_item['brand'] = brand
        product_item['vendor'] = 'PCWorth'
        product_item['category_id'] = category
        product_item['promo'] = item['with_bundle']
        product_item['image'] = item['img_thumbnail']
        product_item['stocks'] = item['stocks_left']
        product_item['warranty'] = None
        product_item['createdAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print('----------------------------------------------------')
        # print(product_item)
        # print('----------------------------------------------------')
        product_items.append(product_item)
        if idx == test_limit and test_limit != 0:
            break

    return product_items


def main(site, category,test_limit, db_save=0):
    with open("./config/api_scraper.yaml", "r") as f:
        configuration = yaml.load(f, Loader=yaml.FullLoader)
        config = configuration[site]
    if site == 'pcworth':
        product_items = pcworth_scraper(category, config, int(test_limit))
        if db_save == 1: database.insertToDatabase(product_items)
        return product_items

# if __name__ == "__main__":
#     print (args)
#     if args.site == 'pcworth':
#         product_items = pcworth_scraper(args.product)
    # database.insertToDatabase(product_items)
        
    # jsonString = json.dumps(product_items, indent=2, separators=(',', ': '), ensure_ascii=False)
    # jsonFile = open(f'{config["filename_prefix"]}_{args.product}.json', "w")
    # jsonFile.write(jsonString)
    # jsonFile.close()

