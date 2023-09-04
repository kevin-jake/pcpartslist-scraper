from playwright.sync_api import sync_playwright
import json
import requests
import re

# URL to open
target_url = "https://www.pcworth.com/product/search/%20?limit=999&category=21&id=+"


auth_token = ''

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
        if request.url == "https://www.api.pcworth.com/api/ecomm/products/available/get?limit=999&category=21&keyword=+":
            auth_token = request.headers['authorization'] 
            if str(auth_token) != 'Bearer null' or  auth_token != '':
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
response = requests.get("https://www.api.pcworth.com/api/ecomm/products/available/get?limit=999&category=21&keyword=+", headers=headers)
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

    product_item['url'] =  "https://www.pcworth.com/product/" + item['slug']
    product_item['name'] = item['product_name']
    product_item['price'] = item['amount']
    product_item['brand'] = brand
    product_item['supplier'] = 'PCWorth'
    product_item['promo'] = item['with_bundle']
    # product_item['warranty'] = response.css('div.MuiBox-root.css-i2n2aa div.MuiBox-root.css-w55c3f p::text').get().strip()
    product_item['stocks'] = item['stocks_left']
    print('----------------------------------------------------')
    print(product_item)
    print('----------------------------------------------------')
    product_items.append(product_item)

jsonString = json.dumps(product_items)
jsonFile = open("pcworth.json", "w")
jsonFile.write(jsonString)
jsonFile.close()

