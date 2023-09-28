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
    db_save = kwargs.get('db_save', 0)
    app.logger.info('Now scraping using: %s, shop: %s, product: %s', scraper, site, product)
    if scraper == 'pchub_scraper':
        params = {
            'spider_name': 'pchub_spider',
            'start_requests': True,
            'crawl_args':json.dumps({'product': product, 'db_save': int(db_save)})
        }
        # TODO: Create dockerfiles to run scrapyrt separately into a container. Make url  an environment variable
        response = requests.get('http://localhost:9080/crawl.json', params)
        data = json.loads(response.text)
        app.logger.info('Scraped: %s of %s product from %s', data['stats']['item_scraped_count'], product, site)
        return data
    elif scraper == 'shopee_scraper':
        params = {
            'spider_name': 'shopee_spider',
            'start_requests': True,
            'crawl_args':json.dumps({'shop': site, 'product': product, 'db_save': int(db_save)})
        }
        # TODO: Create dockerfiles to run scrapyrt separately into a container. Make url  an environment variable
        response = requests.get('http://localhost:9081/crawl.json', params)
        data = json.loads(response.text)
        app.logger.info('Scraped: %s of %s product from %s', data['stats']['item_scraped_count'], product, site)
        return data
    else:
        scraper_module = importlib.import_module(f'scrapers.{scraper}.main')
        product_items = scraper_module.main(site, product, int(db_save))
        app.logger.info('Scraped: %s of %s from %s', len(product_items), product, site)
        return product_items

def scrape_all(scraper, site, products, db_save):
    results = {}
    for product in products:
        results[product] = {}
        try:
            response = scrape(scraper, site=site, product=product, db_save=int(db_save))
            if scraper == 'pchub_scraper' or scraper == 'shopee_scraper':
                if db_save == 0: results[product]['products'] = response['items']
                results[product]['scraped'] = response['stats']['item_scraped_count']
            else:
                if db_save == 0: results[product]['products'] = response
                results[product]['scraped'] = len(response)
        except Exception as e:
            results[product]['error'] = repr(e)
            app.logger.error(repr(e))
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
    except Exception as e:
        return f'{e}', 400

@app.route("/scrape/all")
def scraping_all():
    scrapers_list = [".".join(f.split(".")[:-1]) for f in os.listdir("../config")]
    results = {}
    db_save = request.args.get('db_save', 0)
    for scraper in scrapers_list:
        with open(f"../config/{scraper}.yaml", "r") as f:
            configuration = yaml.load(f, Loader=yaml.FullLoader)
        if scraper == 'pchub_scraper':
            site = 'pchub'
            products = configuration[site]['category']
            results[scraper] = scrape_all(scraper, site, products, db_save)
        elif scraper == 'shopee_scraper':
            for site in configuration['shops']:
                products = configuration['facets']
                results[scraper] = scrape_all(scraper, site, products, db_save)
        elif scraper == 'api_scraper':
            for site in configuration.keys():
                products = configuration[site]['category']
                results[scraper] = scrape_all(scraper, site, products, db_save)
        elif scraper == 'shopify_scraper':
            for site in configuration.keys():
                products = configuration[site]['slug']
                results[scraper] = scrape_all(scraper, site, products, db_save)
    return jsonify(results)