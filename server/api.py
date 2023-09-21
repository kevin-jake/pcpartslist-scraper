from flask import Flask, request, jsonify
import importlib
import requests
import json

app = Flask(__name__)

@app.route("/scrape/<scraper>")
def scrape(scraper):
    site = request.args.get('site', [])
    product = request.args.get('product', [])
    try:
        if scraper == 'pchub_scraper':
            
            params = {
                'spider_name': 'pchub_spider',
                'start_requests': True,
                'crawl_args':json.dumps({'product': product})
            }
            response = requests.get('http://localhost:9080/crawl.json', params)
            data = json.loads(response.text)
            return data
        if scraper == 'shopee_scraper':
            
            params = {
                'spider_name': 'shopee_spider',
                'start_requests': True,
                'crawl_args':json.dumps({'shop': site, 'product': product})
            }
            response = requests.get('http://localhost:9081/crawl.json', params)
            data = json.loads(response.text)
            return data
        else:
            scraper_module = importlib.import_module(f'scrapers.{scraper}.main')
            product_items = scraper_module.main(site, product)
            return jsonify(product_items)
    except ModuleNotFoundError as e:
        return f'scraper "{scraper}" not found! {e}'