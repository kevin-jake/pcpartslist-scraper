# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ShopeeScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class GPUProduct(scrapy. Item):
    id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    brand = scrapy.Field()
    vendor = scrapy. Field()
    category_id= scrapy.Field()
    promo = scrapy. Field(default=None)
    warranty = scrapy. Field(default=None)
    stocks = scrapy.Field(default=None)
    image = scrapy.Field(default=None)
    createdAt = scrapy.Field(default=None)