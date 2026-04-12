import sqlite3
import csv
from datetime import datetime

# Connect to DB
conn = sqlite3.connect('brain.db')
cursor = conn.cursor()

# Process CSV
imported_count = 0
try:
    with open('waitlist.csv', mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp_str = row.get('Timestamp', '').strip()
            name = row.get('Ten', '').strip()
            phone = row.get('So_Dien_Thoai', '').strip()
            email = row.get('Email', '').strip()
            
            # If no name but has email, use email as name
            if not name and email:
                name = email
            elif not name and not email and not phone:
                continue # completely empty row
                
            if not name:
                name = "Khách hàng"
                
            # Convert timestamp format if needed, but let's just keep as string.
            # Zalo is typically phone
            zalo = phone
            
            try:
                cursor.execute(
                    "INSERT INTO customers (name, phone_number, zalo, registration_date) VALUES (?, ?, ?, ?)",
                    (name, phone, zalo, timestamp_str)
                )
                imported_count += 1
            except sqlite3.IntegrityError:
                # If unique constraint fails
                pass
                
    conn.commit()
    print(f"Successfully imported {imported_count} customers from CSV.")
    
    # Let's verify data
    print("--- DATA BẢNG CUSTOMERS ---")
    cursor.execute('SELECT * FROM customers')
    for c in cursor.fetchall():
        print(c)
except Exception as e:
    print("Error during import:", e)

conn.close()
