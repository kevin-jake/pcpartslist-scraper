### Start the python env
```
source venv/bin/activate
```

### Create python env
```
python3 -m venv venv
```

### Running flask app
```
cd server
flask --app api run 
```

### Create a crawler
```
scrapy startproject <crawler name>

e.g.
# This will generate a scraper folder of pcworth_scraper
scrapy startproject pcworth_scraper
```

### Creating a spider
```
scrapy genspider <name_of_spider> <website> 

e.g.
# This will create a spider that will crawl pcworth.com.
scrapy genspider pcworth_spider pcworth.com
```

### Running a spider with an output
**NOTE**: ```-O``` will overwrite the output file and ```-o``` will append results into the ouput file
```
scrapy crawl <spider name> -O <output file> -a <arguments>

e.g.
# This start running the pchub_spider and output the file to pchub.json in the directory where you run this.
scrapy crawl pchub_spider -O pchub.json -a product=GPU 

# Shopee scraper
cd scrapers/shopee_scraper
scrapy crawl shopee_spider -O shopee.json -a shop=pcworx -a product=GPU
```

### Running scrapy shell using a file
```
scrapy shell file://<file path>

e.g.
# This start shell and use the response.html as the substitiue for fetch("url") shell command
scrapy shell file:///home/scraper/response.html
```

### Shopify Scraper

Shop name and product is defined at ```config/shopify_scraper.yaml```

```
cd scrapers/generic_shopify_scraper
python3 main.py -s <site or shop name> -p <product>

e.g.
python3 main.py -s easypc -p GPU
```

### API Scraper

Shop name and product is defined at ```config/api_scraper.yaml```

```
cd scrapers/api_scraper
python3 main.py -s <site or shop name> -p <product>

e.g.
python3 main.py -s pcworth -p GPU
```

### Running the scrapyrt

Port number default is 9080 (currently in use of pchub scraper)

```
scrapyrt -p <port number>

```

### Running Redis

```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

Reference: 
- https://www.youtube.com/watch?v=Q_airdHCuV8
- https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/appengine/flexible_python37_and_earlier/tasks/create_app_engine_queue_task.py
- https://github.com/googlecodelabs/migrate-python2-appengine/blob/master/mod9-py3dstasks/main.py

TODO:
- config yaml is returning an error on the app
- seperate each scraper and create task queues for each scraper
- make request a post method??
- make each scraper route??
- use env variable for google cloud variables