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
def json_model(category):
    if category=='CPU':
        CPU_JSON_FORMAT_PROMPT = '''
            {
            "brand": "",
            "model": "",
            "series": "",
            "base_clock": "",
            "max_clock": "",
            "power_consumption": "",
            "compatible_parts": {
                "motherboard": "AM4",
                "memory": "DDR4",
                "graphics": <array of recommended graphics card that would not have bottleneck>,
                "storage": <array of compatible storage e.g. SATA, NvME, M.2>,
                "cooling": <same as motherboard socket>
            }
            }
            '''
    return CPU_JSON_FORMAT_PROMPT