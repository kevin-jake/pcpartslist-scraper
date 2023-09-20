from dotenv import load_dotenv
load_dotenv()
import os
import MySQLdb

connection = MySQLdb.connect(
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


def insertToDatabase(products):
    product_to_insert = [(d["id"], d["url"], d["name"], d["product_type"], d["brand"], d["supplier"], d["promo"], d["warranty"], d["stocks"], d["image"], d["date_scraped"]) for d in products]
    price_to_insert = [(d["id"], d["price"], d["date_scraped"]) for d in products]

    try:
        insert_product = """insert into PC_PARTS (
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
                )"""
        
        insert_price = """insert into PRICE (
            pc_parts_id_fk, 
            price,
            date_scraped
            ) values (
                %s,
                %s,
                %s
                )"""

        cursor = connection.cursor()
        cursor.executemany(insert_product, product_to_insert)
        cursor.executemany(insert_price, price_to_insert)

        connection.commit()
        print(cursor.rowcount, "Record inserted successfully into PC_PARTS table")

    except MySQLdb.Error as error:
        print("Failed to insert record into MySQL table {}".format(error))

    finally:
        connection.close()