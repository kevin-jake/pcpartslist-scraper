# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from dotenv import load_dotenv
import os
from mysql.connector import connect
from bs4 import BeautifulSoup

load_dotenv()

class ScrapyScraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter['price'] = float(adapter['price'])
        
        # Convert HTML content to string if it exists
        description = adapter.get('description')
        if description:
            # Remove class attributes using BeautifulSoup
            soup = BeautifulSoup(description, 'html.parser')
            for tag in soup.find_all(True):
                tag.attrs = {}
            adapter['description'] = str(soup)
        
        return item


class SaveToMySQLPipeline:

    def __init__(self):
        self.conn = connect(
            host= os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password= os.getenv("DB_PASSWORD"),
            database= os.getenv("DB_NAME"),
        )

        # Create cursor, used to execute commands
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        if spider.db_save == '1':
            self.cur.execute(""" INSERT into Products (
                id, 
                url, 
                name, 
                category_id,
                description,
                brand,
                supplier,
                promo,
                warranty,
                stocks,
                img_url,
                createdAt
                ) values (
                    %s,
                    %s,
                    %s,
                    (select id from Category where name = %s LIMIT 1),
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                    ) ON DUPLICATE KEY UPDATE
                url = VALUES(url),
                name = VALUES(name),
                description = VALUES(description),
                promo = VALUES(promo),
                warranty = VALUES(warranty),
                stocks = VALUES(stocks),
                img_url = VALUES(img_url),
                updatedAt = VALUES(createdAt)""", (
                item["id"],
                item["url"],
                item["name"],
                item["category_id"],
                item["description"],
                item["brand"],
                item["vendor"],
                item["promo"],
                item["warranty"],
                item["stocks"],
                item["image"],
                item["createdAt"],
            ))

            # Define insert statement
            self.cur.execute(""" INSERT into Price (
                pc_parts_id, 
                price,
                createdAt
                ) values (
                    %s,
                    %s,
                    %s
                    )""", (
                item["id"],
                item["price"],
                item["createdAt"],
            ))

            # ## Execute insert of data into database
            self.conn.commit()
        return item

    def close_spider(self, spider):
        # Close cursor & connection to database
        self.cur.close()
        self.conn.close()