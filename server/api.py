from flask import Flask, request, jsonify
import importlib
import requests
import json
import os
import yaml

app = Flask(__name__)

def scrape(scraper,**kwargs):
    site = kwargs.get('site', [])
    product = kwargs.get('product', [])
    save_to_db = kwargs.get('db_save', [])
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
        return product_items

def scrape_all(scraper, site, products, db_save):
    results = {}
    for product in products:
        results[product] = {}
        try:
            if scraper == 'pchub_scraper' or scraper == 'shopee_scraper':
                response = scrape(scraper, site=site, product=product, db_save=db_save)
                results[product]['products'] = response['items']
                results[product]['count'] = response['stats']['item_scraped_count']
            else:
                results[product]['products'] = scrape(scraper, site=site, product=product, db_save=db_save)
                results[product]['count'] = len(results[product]['products'])
        except Exception as e:
            results[product]['error'] = e
            pass 
    return results

@app.route("/scrape/<scraper>")
def scraping(scraper):
    site = request.args.get('site', [])
    product = request.args.get('product', [])
    db_save = request.args.get('db_save', 0)
    try:
        return jsonify(scrape(scraper, site=site, product=product, db_save=db_save))
    except ModuleNotFoundError as e:
        return f'scraper "{scraper}" not found! {e}'

@app.route("/scrape/all")
def scraping_all():
    scrapers_list = [".".join(f.split(".")[:-1]) for f in os.listdir("../config")]
    results = {}
    for scraper in scrapers_list:
        with open(f"../config/{scraper}.yaml", "r") as f:
            configuration = yaml.load(f, Loader=yaml.FullLoader)
        if scraper == 'pchub_scraper':
            site = 'pchub'
            products = configuration[site]['category']
            results[scraper] = scrape_all(scraper, site, products)
        elif scraper == 'shopee_scraper':
            for site in configuration['shops']:
                products = configuration['facets']
                results[scraper] = scrape_all(scraper, site, products)
        elif scraper == 'api_scraper':
            for site in configuration.keys():
                products = configuration[site]['category']
                results[scraper] = scrape_all(scraper, site, products)
        elif scraper == 'shopify_scraper':
            for site in configuration.keys():
                products = configuration[site]['slug']
                results[scraper] = scrape_all(scraper, site, products)
    return jsonify(results)