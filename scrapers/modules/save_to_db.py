from dotenv import load_dotenv
load_dotenv()
import os
from mysql.connector import connect, Error

connection = connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)


def insertToDatabase(products):
    duplicate_count = 0
    updated_count = 0
    new_inserted_count = 0
    item_count = 0

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
        cursor = connection.cursor()

        for product in product_to_insert:
            cursor.execute(
                "SELECT * FROM Products WHERE id = %s", (product[0],)
            )  # Check if product exists

            existing_product = cursor.fetchone()

            if existing_product:
                # Check if properties match except id and createdAt
                if (
                    existing_product[1:-1] == product[1:-1]
                ):  # Skipping id and createdAt for comparison
                    duplicate_count += 1
                else:
                    # Update existing product
                    cursor.execute(
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
                # Insert new product
                cursor.execute(
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
            item_count += 1
            # Insert price
            cursor.execute(
                "INSERT INTO Price (pc_parts_id, price, createdAt) VALUES (%s, %s, %s)",
                (product[0], product[12], product[11]),
            )

        connection.commit()

    except Error as error:
        print("Failed to insert records into MySQL table: {}".format(error))
    finally:
        # Close the cursor
        if 'cursor' in locals() and cursor is not None:
            cursor.close()

        # Close the connection
        if 'connection' in locals() and connection is not None:
            connection.close()

    return duplicate_count, updated_count, new_inserted_count, item_count

def insertToScrapeHistory(task_id, category, shop, status, scrape_start=None, scrape_end=None, elapsed_time=None, results=None ):
    try:
        cursor = connection.cursor()
        cursor.execute(
                "SELECT * FROM Scrape_history WHERE id = %s", (task_id,)
            )  # Check if product exists

        existing_record = cursor.fetchone()

        if existing_record:
            # Update existing product
            cursor.execute(
                """UPDATE Scrape_history
                    SET status = %s,
                        scrape_start = %s,
                        scrape_end = %s,
                        elapsed_time = %s,
                        results = %s
                    WHERE id = %s""",
                (
                    status,
                    scrape_start,
                    scrape_end,
                    elapsed_time,
                    results,
                    task_id
                ),
            )
        else:
            cursor.execute(
                """INSERT INTO Scrape_history (
                        id,
                        category_id,
                        shop,
                        status,
                        scrape_start
                    ) VALUES (
                        %s, 
                        (SELECT id FROM Category WHERE name = %s LIMIT 1), 
                        %s,
                        %s,
                        %s
                    )""",
                
            (   task_id,
                category,        
                shop,
                status,
                scrape_start,
                        ),
            )
        connection.commit()

    except Error as error:
        print("Failed to insert records into MySQL table: {}".format(error))
    finally:
        # Close the cursor
        if 'cursor' in locals() and cursor is not None:
            cursor.close()

        # Close the connection
        if 'connection' in locals() and connection is not None:
            connection.close()
