
from datetime import datetime
import json
import time
from flask import Flask, jsonify, request
import google.auth
from google.cloud import tasks

app = Flask(__name__)
ts_client = tasks.CloudTasksClient()


_, PROJECT_ID = google.auth.default()
REGION_ID = 'asia-southeast1'    # replace w/your own
QUEUE_NAME = 'test-queue'     # replace w/your own
QUEUE_PATH = ts_client.queue_path(PROJECT_ID, REGION_ID, QUEUE_NAME)
PATH_PREFIX = QUEUE_PATH.rsplit('/', 2)[0]

def generate_tasks(scraper, site, product, db_save ):
    'get most recent visits & add task to delete older visits'
    task = {
        'app_engine_http_request': {
            'http_method': tasks.HttpMethod.GET,
            'relative_uri': f'/scrape/{scraper}?site={site}&product={product}&db_save={db_save}&test_limit=5',
        }
    }
    response = ts_client.create_task(parent=QUEUE_PATH, task=task)
    return response

@app.route('/scrape_request/<scraper>')
def scrape_request(scraper):
    response = generate_tasks(scraper, request.args['site'], request.args['product'], request.args['db_save'] )
    return str(response) # need to return SOME string w/200

@app.route('/')
def root():
    'main application (GET) handler'
    return {"success": "ok"}