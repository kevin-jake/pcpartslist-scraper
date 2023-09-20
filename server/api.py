from flask import Flask, request, jsonify
import importlib
import subprocess

app = Flask(__name__)

@app.route("/scrape/<scraper>")
def scrape(scraper):
    site = request.args.get('site', [])
    product = request.args.get('product', [])
    try:
        scraper_module = importlib.import_module(f'scrapers.{scraper}.main')
        product_items = scraper_module.main(site, product)
        return jsonify(product_items)
    except ModuleNotFoundError as e:
        return f'scraper "{scraper}" not found! {e}'