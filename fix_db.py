import sqlite3
import csv

conn = sqlite3.connect('brain.db')
cursor = conn.cursor()

# Clear customers table
cursor.execute('DELETE FROM customers')
conn.commit()

with open('waitlist.csv', mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        timestamp_str = row.get('Timestamp', '').strip()
        name = row.get('Ten', '').strip()
        phone = row.get('So_Dien_Thoai', '').strip()
        email = row.get('Email', '').strip()
        
        if not name and email:
            name = email
        elif not name and not email and not phone:
            continue
            
        if not name:
            name = "Khách hàng"
            
        # Use None instead of empty string for UNIQUE constraint
        phone_val = phone if phone else None
        
        try:
            cursor.execute(
                "INSERT INTO customers (name, phone_number, zalo, registration_date) VALUES (?, ?, ?, ?)",
                (name, phone_val, phone_val, timestamp_str)
            )
        except sqlite3.IntegrityError as e:
            print("Row error:", row, e)

conn.commit()
print("Data re-imported.")
cursor.execute('SELECT * FROM customers')
for c in cursor.fetchall():
    print(c)
conn.close()
