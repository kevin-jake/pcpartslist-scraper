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
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        self.cur = self.conn.cursor()
        self.duplicate_count = 0
        self.update_count = 0
        self.new_item_count = 0

    def process_item(self, item, spider):
        if spider.db_save == 1:
            try:
                self.cur.execute(
                    "SELECT * FROM Products WHERE id = %s", (item["id"],)
                )
                existing_product = self.cur.fetchone()
                print(existing_product)
                print(
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
                )

                if existing_product:
                    if (
                        existing_product[1] == item["url"] and
                        existing_product[2] == item["name"] and
                        existing_product[12] == item["description"] and
                        existing_product[5] == item["promo"] and
                        existing_product[6] == item["warranty"] and
                        existing_product[7] == item["stocks"] and
                        existing_product[8] == item["image"]
                    ):
                        self.duplicate_count += 1
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
                            item["url"],
                            item["name"],
                            item["description"],
                            item["promo"],
                            item["warranty"],
                            item["stocks"],
                            item["image"],
                            item["createdAt"],
                            ),
                        )
                        self.update_count += 1
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
                        (   
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
                            ),
                    )
                    self.new_item_count += 1

                    self.cur.execute(
                        "INSERT INTO Price (pc_parts_id, price, createdAt) VALUES (%s, %s, %s)",
                                (
                            item["id"],
                            item["price"],
                            item["createdAt"],
                        ))

                self.conn.commit()

            except Error as error:
                print("Failed to insert records into MySQL table: {}".format(error))

        return item

    def close_spider(self, spider):

        # Store the counts in the Scrapy stats
        spider.crawler.stats.set_value('duplicates', self.duplicate_count)
        spider.crawler.stats.set_value('updated', self.update_count)
        spider.crawler.stats.set_value('new_items', self.new_item_count)

        # Close cursor & connection to the database
        self.cur.close()
        self.conn.close()