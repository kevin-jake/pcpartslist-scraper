from flask import Flask
from dotenv import load_dotenv
load_dotenv()
import os
from .utils import make_celery
from .api import main

def create_app():
    app = Flask(__name__)
    app.config["CELERY_CONFIG"] = {"broker_url":  os.getenv("RABBITMQ_URL"), "result_backend": os.getenv("REDIS_URL")}

    celery = make_celery(app)
    celery.set_default()
    
    app.register_blueprint(main)

    return app, celery