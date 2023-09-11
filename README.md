### Start the python env
```
source scraper_env/bin/activate
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
scrapy crawl <spider name> -O <output file>

e.g.
# This start running the pcworth_spider and output the file to pcworth.json in the directory where you run this.
scrapy crawl pcworth_spider -O pcworth.json  

# Shopee scraper
cd shopee_scraper
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

Shop name and product is defined at ```generic_shopify_scraper/config.yaml```

```
cd generic_shopify_scraper
python3 scrape_shopify.py -s <site or shop name> -p <product>

e.g.
python3 scrape_shopify.py -s easypc -p GPU
```

