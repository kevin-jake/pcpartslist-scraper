# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from dotenv import load_dotenv
import os
from mysql.connector import connect, Error
from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.signalmanager import dispatcher


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
        self.products_to_insert = []

        self.conn = connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        self.cur = self.conn.cursor()

        # Connect the spider_closed signal to the close_spider method
        dispatcher.connect(self.close_spider, signal=signals.spider_closed)

    def process_item(self, item, spider):
        if spider.db_save == '1':
            self.products_to_insert.append(item)

        return item

    def close_spider(self, spider):
        duplicate_count, updated_count, new_inserted_count = self.insertToDatabase(self.products_to_insert)

        # Store the counts in the Scrapy stats
        spider.crawler.stats.set_value('duplicates', duplicate_count)
        spider.crawler.stats.set_value('updated', updated_count)
        spider.crawler.stats.set_value('new_items', new_inserted_count)

        print(
            f"Number of duplicate products: {duplicate_count}\n"
            f"Number of updated products: {updated_count}\n"
            f"Number of newly inserted products: {new_inserted_count}"
        )

        # Close cursor & connection to the database
        self.cur.close()
        self.conn.close()

    def insertToDatabase(self, products):
        duplicate_count = 0
        updated_count = 0
        new_inserted_count = 0

        product_to_insert = [
            (
                d["id"],
                d["url"],
                d["name"],
                d["category_id"],
                d["description"],
                d["brand"],
                d["vendor"],
                d["promo"],
                d["warranty"],
                d["stocks"],
                d["image"],
                d["createdAt"],
                d["price"]
            )
            for d in products
            if d
        ]

        try:
            for product in product_to_insert:
                self.cur.execute(
                    "SELECT * FROM Products WHERE id = %s", (product[0],)
                )
                existing_product = self.cur.fetchone()

                if existing_product:
                    if existing_product[1:-1] == product[1:-1]:
                        duplicate_count += 1
                    else:
                        self.cur.execute(
                            """UPDATE Products
                               SET url = %s,
                                   name = %s,
                                   description = %s,
                                   promo = %s,
                                   warranty = %s,
                                   stocks = %s,
                                   img_url = %s,
                                   updatedAt = %s
                               WHERE id = %s""",
                            (
                                product[1],
                                product[2],
                                product[4],
                                product[7],
                                product[8],
                                product[9],
                                product[10],
                                product[11],
                                product[0],
                            ),
                        )
                        updated_count += 1
                else:
                    self.cur.execute(
                        """INSERT INTO Products (
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
                            ) VALUES (
                               %s, %s, %s,
                               (SELECT id FROM Category WHERE name = %s LIMIT 1),
                               %s, %s, %s, %s, %s, %s, %s, %s
                            )""",
                        (   product[0],        
                    product[1],
                    product[2],
                    product[3],
                    product[4],
                    product[5],
                    product[6],
                    product[7],
                    product[8],
                    product[9],
                    product[10],
                    product[11],
                            ),
                    )
                    new_inserted_count += 1

                self.cur.execute(
                    "INSERT INTO Price (pc_parts_id, price, createdAt) VALUES (%s, %s, %s)",
                    (product[0], product[12], product[11]),
                )

            self.conn.commit()

        except Error as error:
            print("Failed to insert records into MySQL table: {}".format(error))

        return duplicate_count, updated_count, new_inserted_count