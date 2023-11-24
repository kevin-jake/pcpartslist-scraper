import google.generativeai as palm
from dotenv import load_dotenv
load_dotenv()
import os
palm.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))

from google.api_core import retry

@retry.Retry()
def generate_text(*args, **kwargs):
  return palm.generate_text(*args, **kwargs)

def get_specs(product, json_model):
    prompt_template = """
        You are a computer parts expert and you always know the specification of computer parts. Here's one:

         {product}

        Using the information provided display the specification of that product in JSON format like this: {json_model}

        The specification in a specific JSON format:
        """
    completion = generate_text(
                model='models/text-bison-001',
                prompt=prompt_template.format(product=product, json_model=json_model),
                # The maximum length of the response
                max_output_tokens=800,
                )

    return completion.result

if __name__ == "__main__":
#    TODO: Replace this with the model in the __init__.py config directory and integrate to the scrapers. Think on how to store the data in the database or to switch to NoSQL
   json_test = '''
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
   result = get_specs('AMD A6-9500 A6-Series APU for Desktops (Up to 3.8GHz)',json_test)
   print(result)