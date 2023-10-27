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
            CREATE TABLE `Products` (
                `id` varchar(255) NOT NULL,
                `url` varchar(255),
                `name` text,
                `brand` varchar(255),
                `supplier` varchar(255),
                `promo` varchar(255),
                `warranty` varchar(255),
                `stocks` varchar(255),
                `img_url` varchar(255),
                `createdAt` datetime(3) DEFAULT current_timestamp(3),
                `updatedAt` datetime(3),
                `category_id` int,
                PRIMARY KEY (`id`),
                KEY `Products_category_id_idx` (`category_id`)
            )
        """)

        self.cur.execute("""
            CREATE TABLE `Price` (
                `id` int NOT NULL AUTO_INCREMENT,
                `price` decimal(10,0),
                `createdAt` datetime(3) DEFAULT current_timestamp(3),
                `updatedAt` datetime(3),
                `pc_parts_id` varchar(255) NOT NULL,
                PRIMARY KEY (`id`),
                KEY `Price_pc_parts_id_idx` (`pc_parts_id`)
            )
        """)

        self.cur.execute("""
            CREATE TABLE `Category` (
                `id` int NOT NULL AUTO_INCREMENT,
                `name` varchar(255) NOT NULL,
                `description` varchar(255),
                `createdAt` datetime(3) DEFAULT current_timestamp(3),
                `updatedAt` datetime(3),
                PRIMARY KEY (`id`)
            )
        """)

    def process_item(self, item, spider):
        if spider.db_save == '1':
            self.cur.execute(""" INSERT into Products (
                id, 
                url, 
                name, 
                category_id, 
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
                    %s
                    ) ON DUPLICATE KEY UPDATE
                url = VALUES(url),
                name = VALUES(name),
                promo = VALUES(promo),
                warranty = VALUES(warranty),
                stocks = VALUES(stocks),
                img_url = VALUES(img_url),
                updatedAt = VALUES(createdAt)""", (
                item["id"],
                item["url"],
                item["name"],
                item["category_id"],
                item["brand"],
                item["supplier"],
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