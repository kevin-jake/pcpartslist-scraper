import os
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
    # app.logger.info('Now scraping using: %s, shop: %s, product: %s', scraper, site, product)
    if scraper == 'scrapy_scraper':
        params = {
            'spider_name': f'{site}_spider',
            'start_requests': True,
            'crawl_args':json.dumps({'shop': site, 'product': product, 'db_save': int(db_save)})
        }
        response = requests.get(f'http://{os.environ.get("SCRAPY_SCRAPER")}:9080/crawl.json', params)
        data = json.loads(response.text)
        # app.logger.info('Scraped: %s of %s product from %s', data['stats']['item_scraped_count'], product, site)
        return data
    else:
        try:
            scraper_module = importlib.import_module(f'scrapers.{scraper}.main')
            product_items = scraper_module.main(site, product, int(test_limit or 0), int(db_save))
            # app.logger.info('Scraped: %s of %s from %s', len(product_items), product, site)
        except KeyError as e:
            product_items = f'{site} not found on {scraper}'
        finally:
            return product_items
                        