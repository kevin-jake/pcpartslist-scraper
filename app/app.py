from flask import Flask, request, jsonify
from .worker import celery
import time

app = Flask(__name__)



# def scrape_all(scraper, site, products, db_save):
#     results = {}
#     for product in products:
#         results[product] = {}
#         try:
#             response = scrape(scraper, site=site, product=product, db_save=int(db_save))
#             if scraper == 'pchub_scraper' or scraper == 'shopee_scraper':
#                 if db_save == 0: results[product]['products'] = response['items']
#                 results[product]['scraped'] = response['stats']['item_scraped_count']
#             else:
#                 if db_save == 0: results[product]['products'] = response
#                 results[product]['scraped'] = len(response)
#         except Exception as e:
#             results[product]['error'] = repr(e)
#             app.logger.error(repr(e))
#             pass 
#     return results

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'scraper-status': 'OK'})

@app.route('/scrape/<scraper>', methods=['GET'])
def scrape(scraper):
    running = celery.send_task('scrape', kwargs={'scraper': scraper, "args": request.args})
    time.sleep(1)
    res = celery.AsyncResult(running.id)
    if res.status != 'PENDING':
        return jsonify({"task_id": running.id, "status": res.status, "result": res.result})
    return jsonify({"task_id": running.id, "status": res.status})

@app.route('/status/<task_id>', methods=['GET'])
def getStatus(task_id):
    res = celery.AsyncResult(task_id)
    if res.status != 'PENDING':
        print(res.result)
        return jsonify({"task_id": task_id, "status": res.status, "result": res.result})
    return jsonify({"task_id": task_id, "status": res.status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# @app.route("/scrape/all")
# def scraping_all():
#     scrapers_list = [".".join(f.split(".")[:-1]) for f in os.listdir("../config")]
#     results = {}
#     db_save = request.args.get('db_save', 0)
#     for scraper in scrapers_list:
#         with open(f"../config/{scraper}.yaml", "r") as f:
#             configuration = yaml.load(f, Loader=yaml.FullLoader)
#         if scraper == 'pchub_scraper':
#             site = 'pchub'
#             products = configuration[site]['category']
#             results[scraper] = scrape_all(scraper, site, products, db_save)
#         elif scraper == 'shopee_scraper':
#             for site in configuration['shops']:
#                 products = configuration['facets']
#                 results[scraper] = scrape_all(scraper, site, products, db_save)
#         elif scraper == 'api_scraper':
#             for site in configuration.keys():
#                 products = configuration[site]['category']
#                 results[scraper] = scrape_all(scraper, site, products, db_save)
#         elif scraper == 'shopify_scraper':
#             for site in configuration.keys():
#                 products = configuration[site]['slug']
#                 results[scraper] = scrape_all(scraper, site, products, db_save)
#     return jsonify(results)