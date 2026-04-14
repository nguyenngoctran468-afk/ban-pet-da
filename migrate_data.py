import sqlite3
import requests
import json

import os
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://aahbbepwytfpuzjuxocv.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def migrate_table(conn, table_name, columns):
    c = conn.cursor()
    c.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
    rows = c.fetchall()
    
    if not rows:
        print(f"Bảng {table_name} đang trống, bỏ qua.")
        return
        
    print(f"Đang đồng bộ {len(rows)} bản ghi của bảng {table_name}...")
    
    records_to_insert = []
    for row in rows:
        record = {}
        for i, col in enumerate(columns):
            val = row[i]
            if col == 'phone_number' and val is None:
                val = f"UNAVAILABLE_{row[0]}"
            record[col] = val
        records_to_insert.append(record)
        
    # Xoá data cũ trước khi chèn lại
    requests.delete(f"{SUPABASE_URL}/rest/v1/{table_name}?id=gt.0", headers=headers)
        
    # Send to Supabase
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    res = requests.post(url, headers=headers, json=records_to_insert)
    
    if res.status_code in [200, 201]:
        print(f"✅ Hoàn thành bảng {table_name}!")
    else:
        print(f"❌ Lỗi bảng {table_name}: {res.text}")

def main():
    conn = sqlite3.connect('brain.db')
    
    # Thứ tự chèn quan trọng (do khoá ngoại constraint)
    # 1. Products
    migrate_table(conn, 'products', ['id', 'name', 'price', 'description', 'stock'])
    
    # 2. Customers
    migrate_table(conn, 'customers', ['id', 'name', 'phone_number', 'zalo', 'registration_date'])
    
    # 3. Orders
    migrate_table(conn, 'orders', ['id', 'customer_id', 'product_id', 'amount', 'status', 'payment_method', 'order_date'])
    
    conn.close()
    print("🚀 DI TRÚ DI LIỆU THÀNH CÔNG!")

if __name__ == "__main__":
    main()
