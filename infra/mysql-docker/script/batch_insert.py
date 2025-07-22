import mysql.connector
from mysql.connector import Error
import random

def generate_books_data(num):
    books = []
    for i in range(1, num + 1):
        title = f"Book {i}"
        author = f"Author {random.randint(1, 100)}"
        price = round(random.uniform(5, 100), 2)
        stock = random.randint(0, 50)
        books.append((title, author, price, stock))
    return books

def batch_insert_books(table_name, books, batch_size=1000):
    try:
        connection = mysql.connector.connect(
            host='localhost',       # 改成你的MySQL地址
            user='admin',           # 改成你的用户名
            password='123456',      # 改成你的密码
            database='bookstore'    # 改成你的数据库名
        )
        cursor = connection.cursor()
        # 用 f-string 拼接表名（请确认 table_name 是受信任的，防止SQL注入）
        sql = f"INSERT INTO {table_name} (title, author, price, stock) VALUES (%s, %s, %s, %s)"

        for i in range(0, len(books), batch_size):
            batch = books[i:i + batch_size]
            cursor.executemany(sql, batch)
            connection.commit()
            print(f"Inserted batch {i // batch_size + 1} ({len(batch)} records)")

    except Error as e:
        print("Error while connecting or inserting:", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    total_records = 1000000  # 你想插入多少条测试数据
    books_data = generate_books_data(total_records)
    batch_insert_books("books_1", books_data)
    batch_insert_books("books_2", books_data)
