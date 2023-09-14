# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from dotenv import load_dotenv
load_dotenv()
import os
import MySQLdb





class PchubScraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter['price'] = float(adapter['price'])

        return item


class SaveToMySQLPipeline:

    def __init__(self):
        self.conn = MySQLdb.connect(
            host= os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            passwd= os.getenv("DB_PASSWORD"),
            db= os.getenv("DB_NAME"),
            autocommit = True,
            ssl_mode = "VERIFY_IDENTITY",
            ssl      = {
                "ca": "/etc/ssl/certs/ca-certificates.crt"
            }
        )

        # Create cursor, used to execute commands
        self.cur = self.conn.cursor()

        # Create books table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS PC_PARTS(
            pc_parts_id_pk VARCHAR(255) NOT NULL, 
            url VARCHAR(255),
            name text,
            product_type VARCHAR(255),
            brand VARCHAR(255),
            supplier VARCHAR(255),
            promo VARCHAR(255),
            warranty VARCHAR(255),
            stocks VARCHAR(255),
            img_url VARCHAR(255),
            date_scraped DATE,
            PRIMARY KEY (pc_parts_id_pk)
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS PRICE(
            price_id_pk int NOT NULL auto_increment, 
            price DECIMAL,
            date_scraped DATE,
            pc_parts_id_fk VARCHAR(255),
            PRIMARY KEY (price_id_pk),
            KEY pc_parts_id_idx (pc_parts_id_fk)
        )
        """)

    def process_item(self, item, spider):

        # Define insert statement
        self.cur.execute(""" INSERT IGNORE into PC_PARTS (
            pc_parts_id_pk, 
            url, 
            name, 
            product_type, 
            brand,
            supplier,
            promo,
            warranty,
            stocks,
            img_url,
            date_scraped
            ) values (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
                )""", (
            item["id"],
            item["url"],
            item["name"],
            item["product_type"],
            item["brand"],
            item["supplier"],
            item["promo"],
            item["warranty"],
            item["stocks"],
            item["image"],
            item["date_scraped"],
        ))

        # Define insert statement
        self.cur.execute(""" INSERT IGNORE into PRICE (
            pc_parts_id_fk, 
            price,
            date_scraped
            ) values (
                %s,
                %s,
                %s
                )""", (
            item["id"],
            item["price"],
            item["date_scraped"],
        ))

        # ## Execute insert of data into database
        self.conn.commit()
        return item

    def close_spider(self, spider):
        # Close cursor & connection to database
        self.cur.close()
        self.conn.close()