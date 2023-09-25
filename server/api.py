from flask import Flask, request, jsonify
import importlib
import requests
import json

app = Flask(__name__)

def scrapers(scraper,**kwargs):
    site = kwargs.get('site', [])
    product = kwargs.get('product', [])
    if scraper == 'pchub_scraper':
        params = {
            'spider_name': 'pchub_spider',
            'start_requests': True,
            'crawl_args':json.dumps({'product': product})
        }
        # TODO: Create dockerfiles to run scrapyrt separately into a container. Make url  an environment variable
        response = requests.get('http://localhost:9080/crawl.json', params)
        data = json.loads(response.text)
        return data
    if scraper == 'shopee_scraper':
        
        params = {
            'spider_name': 'shopee_spider',
            'start_requests': True,
            'crawl_args':json.dumps({'shop': site, 'product': product})
        }
        # TODO: Create dockerfiles to run scrapyrt separately into a container. Make url  an environment variable
        response = requests.get('http://localhost:9081/crawl.json', params)
        data = json.loads(response.text)
        return data
    else:
        scraper_module = importlib.import_module(f'scrapers.{scraper}.main')
        product_items = scraper_module.main(site, product)
        return jsonify(product_items)

@app.route("/scrape/<scraper>")
def scrape(scraper):
    site = request.args.get('site', [])
    product = request.args.get('product', [])
    try:
        return scrapers(scraper, site=site, product=product)
    except ModuleNotFoundError as e:
        return f'scraper "{scraper}" not found! {e}'