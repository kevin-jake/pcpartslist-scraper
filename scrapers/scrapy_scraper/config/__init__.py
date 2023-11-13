# config/__init__.py
import os
import yaml

# Get the directory where this __init__.py file is located
current_directory = os.path.dirname(__file__)


with open(os.path.join(current_directory, 'scrapy_scraper.yaml'), 'r') as f:
    scrapy_scraper_config = yaml.load(f, Loader=yaml.FullLoader)
    pchub_scraper_config = scrapy_scraper_config['pchub']
    shopee_scraper_config = scrapy_scraper_config['shopee']

