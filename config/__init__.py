# config/__init__.py
import os
import yaml

# Get the directory where this __init__.py file is located
current_directory = os.path.dirname(__file__)

# Load each YAML file and store its content in a variable
with open(os.path.join(current_directory, 'api_scraper.yaml'), 'r') as f:
    api_scraper_config = yaml.load(f, Loader=yaml.FullLoader)

with open(os.path.join(current_directory, 'shopify_scraper.yaml'), 'r') as f:
    shopify_scraper_config = yaml.load(f, Loader=yaml.FullLoader)

with open(os.path.join(current_directory, 'app_config.yaml'), 'r') as f:
    app_scraper_config = yaml.load(f, Loader=yaml.FullLoader)
