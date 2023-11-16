from dotenv import load_dotenv
load_dotenv()
import os
from mysql.connector import connect, Error

connection = connect(
            host= os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password= os.getenv("DB_PASSWORD"),
            database= os.getenv("DB_NAME"),
        )


def insertToDatabase(products):
    product_to_insert = [(d["id"], d["url"], d["name"], d["category_id"], d['description'], d["brand"], d["vendor"], d["promo"], d["warranty"], d["stocks"], d["image"], d["createdAt"]) for d in products if d]
    price_to_insert = [(d["id"], d["price"], d["createdAt"]) for d in products if d]
    try:
        insert_product = """insert into Products (
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
                updatedAt = VALUES(createdAt)"""
        
        insert_price = """insert into Price (
            pc_parts_id, 
            price,
            createdAt
            ) values (
                %s,
                %s,
                %s
                )"""

        cursor = connection.cursor()
        cursor.executemany(insert_product, product_to_insert)
        cursor.executemany(insert_price, price_to_insert)

        connection.commit()

    except Error as error:
        print("Failed to insert record into MySQL table {}".format(error))

    finally:
        # Close the cursor
        if 'cursor' in locals() and cursor is not None:
            cursor.close()

        # Close the connection
        if 'connection' in locals() and connection is not None:
            connection.close()
