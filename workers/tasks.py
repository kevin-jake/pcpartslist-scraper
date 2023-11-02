import requests
import json
import importlib
import time
import scrapers
from celery import shared_task
from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_logger

logger = get_logger(__name__)

@shared_task(bind=True, base=AbortableTask)
def scrape(self, scraper,**kwargs):
    args = kwargs.get('args')
    site = args.get('site', [])
    product = args.get('product', [])
    db_save = args.get('db_save', 0)
    test_limit = args.get('test_limit', None)
    if scraper == 'pchub_scraper':
        params = {
            'spider_name': 'pchub_spider',
            'start_requests': True,
            'crawl_args':json.dumps({'product': product, 'db_save': int(db_save)})
        }
        response = requests.get('http://localhost:9080/crawl.json', params)
        data = json.loads(response.text)
        logger.info('Scraped: %s of %s product from %s', data['stats']['item_scraped_count'], product, site)
        return data
    elif scraper == 'shopee_scraper':
        params = {
            'spider_name': 'shopee_spider',
            'start_requests': True,
            'crawl_args':json.dumps({'shop': site, 'product': product, 'db_save': int(db_save)})
        }
        response = requests.get('http://localhost:9081/crawl.json', params)
        data = json.loads(response.text)
        logger.info('Scraped: %s of %s product from %s', data['stats']['item_scraped_count'], product, site)
        return data
    else:
        scraper_module = importlib.import_module(f'scrapers.{scraper}.main')
        product_items = scraper_module.main(site, product, int(test_limit or 0), int(db_save or 0))
        logger.info('Scraped: %s of %s from %s', len(product_items), product, site)
        return product_items