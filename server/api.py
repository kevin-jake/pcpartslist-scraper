from flask import Blueprint, request, jsonify
from workers.tasks import scrape
from celery.result import AsyncResult

main = Blueprint('main', __name__)


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
#             main.logger.error(repr(e))
#             pass 
#     return results

@main.route("/scrape/<scraper>")
def scraping(scraper):
    try:
        response = scrape.delay(scraper,args=request.args)
        # return jsonify(scrape(scraper, args=request.args))
        print(response)
        return response.task_id
    except ModuleNotFoundError as e:
        return f'Scraper "{scraper}" not found! {e}'
    except Exception as e:
        return f'{e}', 400

@main.route("/status/<task_id>")
def result(task_id):
    result = scrape.AsyncResult(task_id)
    print(result)
    return result.status

# @main.route("/scrape/all")
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