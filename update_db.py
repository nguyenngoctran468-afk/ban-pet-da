import sqlite3

def update():
    conn = sqlite3.connect('brain.db')
    cursor = conn.cursor()
    
    # 1. Add payment_method column if not exists
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT DEFAULT 'auto'")
        print("Added column 'payment_method'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'payment_method' already exists.")
        else:
            print("Error adding column:", e)
            
    # 2. Map existing statuses
    # 'Chờ thanh toán' -> pending
    # 'Đã thanh toán (Sepay)' or 'Đã thanh toán' -> success
    # 'Đã giao hàng' -> success
    
    cursor.execute("UPDATE orders SET status = 'pending' WHERE status LIKE '%Chờ thanh toán%'")
    cursor.execute("UPDATE orders SET status = 'success' WHERE status LIKE '%Đã thanh toán%'")
    cursor.execute("UPDATE orders SET status = 'success' WHERE status LIKE '%Đã giao hàng%'")
    
    # Also default old successful orders to auto, pending to auto
    cursor.execute("UPDATE orders SET payment_method = 'auto' WHERE payment_method IS NULL")
    
    conn.commit()
    print("Database schema and statuses updated successfully.")
    conn.close()

if __name__ == '__main__':
    update()
