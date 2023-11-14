import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from celery import Celery
import importlib
from scrapers import *
import requests
import json

CELERY_BROKER = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

celery =  Celery('tasks', broker=CELERY_BROKER, backend=CELERY_BACKEND)


@celery.task(name='scrape', trail=True)
def scrape(**kwargs):
    scraper = kwargs.get('scraper')
    args = kwargs.get('args')
    site = args.get('site', [])
    product = args.get('product', [])
    db_save = args.get('db_save', 0)
    test_limit = args.get('test_limit', None)
    result = args.get('result', 'simple')

    if scraper == 'scrapy_scraper':
        shop = site
        spider = site
        fullsite = site.split('-')
        if len(fullsite) > 1:
            spider = fullsite[0]
            shop = fullsite[1]
        params = {
            'spider_name': f'{spider}_spider',
            'start_requests': True,
            'crawl_args':json.dumps({ 'shop': shop, 'product': product, 'db_save': int(db_save)})
        }
        response = requests.get(f'{os.environ.get("SCRAPY_SCRAPER", "http://localhost:9080/")}crawl.json', params)
        data = json.loads(response.text)
        # app.logger.info('Scraped: %s of %s product from %s', data['stats']['item_scraped_count'], product, site)
        if result == 'simple':
            return {'shop': site, 'product': product, 'items_scraped_count': data['stats']['item_scraped_count']}
        return data
    else:
        try:
            scraper_module = importlib.import_module(f'scrapers.{scraper}.main')
            product_items = scraper_module.main(site, product, int(test_limit or 0), int(db_save))
            if result == 'simple':
                product_items = {'shop': site, 'product': product, 'items_scraped_count': len(product_items)}
            # app.logger.info('Scraped: %s of %s from %s', len(product_items), product, site)
        except KeyError as e:
            product_items = f'{site} not found on {scraper}'
        except ModuleNotFoundError as e:
            product_items = f'{scraper} not found on this project'
        finally:
            return product_items
                        