import sqlite3
import json
import os
from datetime import datetime

# Connect to database
db_path = 'brain.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Create products
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    stock INTEGER DEFAULT 0
)
''')

# 2. Create customers
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_number TEXT UNIQUE,
    zalo TEXT,
    registration_date TEXT
)
''')

# 3. Create orders
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product_id INTEGER,
    amount REAL,
    status TEXT,
    payment_method TEXT DEFAULT 'auto',
    order_date TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
)
''')
conn.commit()

# Import waitlist.json if exists
if os.path.exists('waitlist.json'):
    try:
        with open('waitlist.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            name = item.get('Ten', 'Unknown')
            phone = item.get('So_Dien_Thoai', '')
            zalo = phone # using phone as zalo
            date_str = item.get('Timestamp', datetime.now().isoformat())
            try:
                cursor.execute('INSERT OR IGNORE INTO customers (name, phone_number, zalo, registration_date) VALUES (?, ?, ?, ?)',
                               (name, phone, zalo, date_str))
            except sqlite3.Error as e:
                print(f"Error inserting customer {name}: {e}")
        conn.commit()
    except Exception as e:
        print("Error reading waitlist.json:", e)
else:
    # Maybe try reading from data/ directory
    if os.path.exists('data/waitlist.json'):
        with open('data/waitlist.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            name = item.get('Ten', 'Unknown')
            phone = item.get('So_Dien_Thoai', '')
            try:
                cursor.execute('INSERT OR IGNORE INTO customers (name, phone_number, zalo, registration_date) VALUES (?, ?, ?, ?)',
                           (name, phone, phone, datetime.now().isoformat()))
            except sqlite3.Error:
                pass
        conn.commit()

# Query and print out tables
print("=== PRODUCTS ===")
cursor.execute('SELECT * FROM products')
print(cursor.fetchall())

print("=== CUSTOMERS ===")
cursor.execute('SELECT * FROM customers')
print(cursor.fetchall())

print("=== ORDERS ===")
cursor.execute('SELECT * FROM orders')
print(cursor.fetchall())

conn.close()
