import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from celery import Celery, current_task
from celery.utils.log import get_task_logger
import importlib
from scrapers import *
import requests
import json
import base64
from contextlib import contextmanager
import pickle as pkl
import uuid

from redis import StrictRedis
from redis_cache import Cache
from redlock import RedLock
import time


CELERY_BROKER = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

logger = get_task_logger(__name__)

rds = StrictRedis('localhost', decode_responses=True, charset="utf-8")
rds_cache = StrictRedis('localhost', decode_responses=False, charset="utf-8")
redis_cache = Cache(redis_client=rds_cache, prefix="rc", serializer=pkl.dumps, deserializer=pkl.loads)
dlm = RedLock([{"host": 'localhost'}])

DEFAULT_CACHE_EXPIRATION = 24 * 60 * 60  # by default keep cached values around 1 day

REMOVE_ONLY_IF_OWNER_SCRIPT = """
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end
"""

celery =  Celery('tasks', broker=CELERY_BROKER, backend=CELERY_BACKEND)

@contextmanager
def redis_lock(lock_name, expires=60):
    # https://breadcrumbscollector.tech/what-is-celery-beat-and-how-to-use-it-part-2-patterns-and-caveats/
    task_id = current_task.request.id if current_task else None
    random_value = str(task_id or uuid.uuid4())
    lock_acquired = bool(
        rds.set(lock_name, random_value, ex=expires, nx=True)
    )
    print(f'Lock acquired? {lock_name} for {expires} - {lock_acquired}')

    yield lock_acquired

    if lock_acquired:
        # if lock was acquired, then try to release it BUT ONLY if we are the owner
        # (i.e. value inside is identical to what we put there originally)
        rds.eval(REMOVE_ONLY_IF_OWNER_SCRIPT, 1, lock_name, random_value)
        print(f'Lock {lock_name} released!')


def argument_signature(*args, **kwargs):
    arg_list = [str(x) for x in args]
    kwarg_list = [f"{str(k)}:{str(v)}" for k, v in kwargs.items()]
    return base64.b64encode(f"{'_'.join(arg_list)}-{'_'.join(kwarg_list)}".encode()).decode()


def task_lock(func=None, main_key="", timeout=DEFAULT_CACHE_EXPIRATION):
    def _dec(run_func):
        def _caller(*args, **kwargs):
            lock_id=f"{main_key}_{argument_signature(*args, **kwargs)}"
            with redis_lock(lock_id, timeout) as acquired:
                if not acquired:
                    return {
                        "message": "Task execution skipped -- another task already has the lock",
                        "task_id": rds.get(lock_id),
                    }
                return run_func(*args, **kwargs)
        return _caller
    return _dec(func) if func is not None else _dec


def unpack_redis_json(key: str):
    result = rds.get(key)
    if result is not None:
        return json.loads(result)


@celery.task(name='scrape', trail=True)
@task_lock(main_key="scrape")
def scrape(**kwargs):
    scraper = kwargs.get('scraper')
    args = kwargs.get('args')
    site = args.get('site', [])
    product = args.get('product', [])
    db_save = args.get('db_save', 0)
    test_limit = args.get('test_limit', None)
    result = args.get('result', 'simple')
    time.sleep(120)

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
                        