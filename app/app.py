from flask import Flask, request, jsonify
from .worker import celery
import time
from config import app_scraper_config

app = Flask(__name__)




@app.route('/', methods=['GET'])
def health_check():
    response = jsonify({'scraper-status': 'OK'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/scrape/<scraper>', methods=['GET'])
def scrape(scraper):
    running = celery.send_task('scrape', kwargs={'scraper': scraper, "args": request.args})
    time.sleep(1)
    res = celery.AsyncResult(running.id)
    if res.status != 'PENDING':
        if isinstance(res.result, dict) and res.result['task_id']:
                task_id = res.result['task_id']
                realTask = celery.AsyncResult(task_id)
                response = jsonify({"task_id": task_id, "status": realTask.status})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
        response = jsonify({"task_id": running.id, "status": res.status, "result": res.result})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    response = jsonify({"task_id": running.id, "status": res.status})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/status/<task_id>', methods=['GET'])
def getStatus(task_id):
    res = celery.AsyncResult(task_id)
    if res.status != 'PENDING':
        print(res.result)
        response = jsonify({"task_id": task_id, "status": res.status, "result": res.result})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    response = jsonify({"task_id": task_id, "status": res.status})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(repr(e))
    response = jsonify(error=str(e)), 500
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

@app.route("/scrape/all")
def scraping_all():
    scrapers = app_scraper_config['scrapers']
    products = app_scraper_config['products']
    db_save = request.args.get("db_save", 0)
    # args
    # scraper = kwargs.get('scraper')
    # args = kwargs.get('args')
    # site = args.get('site', [])
    # product = args.get('product', [])
    # db_save = args.get('db_save', 0)
    # test_limit = args.get('test_limit', None)
    # format = args.get('format', 'simple')
    ret = []
    response = {}
    for scraper in scrapers:
        shops = scrapers[scraper]
        app.logger.info('------------ SCRAPING USING %s --------------', scraper)
        for shop in shops:
            app.logger.info('------------ SCRAPING %s --------------', shop.upper())
            for product in products:
                app.logger.info('------------ SCRAPING %s product: %s--------------', shop.upper(), product)
                args = {"site": shop, "product": product, "db_save": db_save  }
                running = celery.send_task('scrape', kwargs={'scraper': scraper, "args": args})
                time.sleep(1)
                res = celery.AsyncResult(running.id)
                if res.status != 'PENDING':
                    print(res.result.get('task_id', False))
                    if isinstance(res.result, dict) and res.result.get('task_id', False):
                            task_id = res.result['task_id']
                            realTask = celery.AsyncResult(task_id)
                            response = {"site": shop, "product": product, "task_id": task_id, "status": realTask.status}
                    response = {"site": shop, "product": product, "task_id": running.id, "status": res.status, "result": res.result}
                else:
                    response = {"site": shop, "product": product, "task_id": running.id, "status": res.status}
                app.logger.info('Result: %s', response)
                ret.append(response)
    response = jsonify(ret)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response