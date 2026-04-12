from flask import Flask, render_template, request, redirect, url_for, g, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app) # ENABLE CORS FOR NGROK
DATABASE = 'brain.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Serves main site
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/admin')
def admin():
    tab = request.args.get('tab', 'products')
    db = get_db()
    
    products = db.execute('SELECT * FROM products').fetchall()
    customers = db.execute('SELECT * FROM customers').fetchall()
    orders = db.execute('''
        SELECT orders.*, customers.name as customer_name, products.name as product_name 
        FROM orders 
        LEFT JOIN customers ON orders.customer_id = customers.id 
        LEFT JOIN products ON orders.product_id = products.id
        ORDER BY orders.id DESC
    ''').fetchall()
    
    return render_template('admin.html', tab=tab, products=products, customers=customers, orders=orders)

# ------------- PRODUCTS -------------
@app.route('/admin/product/add', methods=['POST'])
def add_product():
    name = request.form['name']
    price = request.form['price']
    description = request.form['description']
    stock = request.form['stock']
    db = get_db()
    db.execute('INSERT INTO products (name, price, description, stock) VALUES (?, ?, ?, ?)', (name, price, description, stock))
    db.commit()
    return redirect(url_for('admin', tab='products'))

@app.route('/admin/product/delete/<int:id>')
def delete_product(id):
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('admin', tab='products'))

# ------------- CUSTOMERS -------------
@app.route('/admin/customer/add', methods=['POST'])
def add_customer():
    name = request.form['name']
    phone = request.form['phone']
    zalo = request.form['zalo']
    date = request.form['date']
    db = get_db()
    try:
        db.execute('INSERT INTO customers (name, phone_number, zalo, registration_date) VALUES (?, ?, ?, ?)', (name, phone, zalo, date))
        db.commit()
    except Exception as e:
        print("Lỗi:", e)
    return redirect(url_for('admin', tab='customers'))

@app.route('/admin/customer/delete/<int:id>')
def delete_customer(id):
    db = get_db()
    db.execute('DELETE FROM customers WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('admin', tab='customers'))

# ------------- ORDERS -------------
@app.route('/admin/order/add', methods=['POST'])
def add_order():
    if not request.form.get('customer_id') or not request.form.get('product_id'):
        return redirect(url_for('admin', tab='orders'))
        
    customer_id = request.form['customer_id']
    product_id = request.form['product_id']
    amount = request.form['amount']
    status = request.form['status']
    order_date = request.form['order_date']
    
    db = get_db()
    # Insert order
    db.execute('INSERT INTO orders (customer_id, product_id, amount, status, payment_method, order_date) VALUES (?, ?, ?, ?, ?, ?)', 
               (customer_id, product_id, amount, status, 'manual', order_date))
               
    # Deduct stock "tự động trừ số lượng sản phẩm"
    db.execute('UPDATE products SET stock = stock - 1 WHERE id = ?', (product_id,))
    
    db.commit()
    return redirect(url_for('admin', tab='orders'))

@app.route('/admin/order/delete/<int:id>')
def delete_order(id):
    db = get_db()
    db.execute('DELETE FROM orders WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('admin', tab='orders'))

@app.route('/admin/order/update/<int:id>', methods=['POST'])
def update_order(id):
    status = request.form.get('status')
    if status in ['success', 'cancelled', 'pending']:
        db = get_db()
        
        # Lấy thông tin đơn hàng hiện tại
        order = db.execute('SELECT * FROM orders WHERE id = ?', (id,)).fetchone()
        if not order:
            return redirect(url_for('admin', tab='orders'))
            
        old_status = order['status']
        
        db.execute("UPDATE orders SET status = ?, payment_method = 'manual' WHERE id = ?", (status, id))
        
        # Nếu chuyển sang cancelled, và trạng thái cũ không phải là cancelled, thì hoàn kho
        if status == 'cancelled' and old_status != 'cancelled':
            db.execute('UPDATE products SET stock = stock + 1 WHERE id = ?', (order['product_id'],))
        
        # Nếu từ cancelled chuyển lại thành success/pending, thì trừ kho đi 1 lại
        if status != 'cancelled' and old_status == 'cancelled':
            db.execute('UPDATE products SET stock = stock - 1 WHERE id = ?', (order['product_id'],))
            
        db.commit()
    return redirect(url_for('admin', tab='orders'))


from datetime import datetime
from flask import jsonify

# ------------- THỰC TẾ CHECKOUT FLOW -------------
@app.route('/checkout')
@app.route('/thanh-toan')
def checkout():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    return render_template('checkout.html', products=products)

@app.route('/api/create_order', methods=['POST'])
def api_create_order():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    product_id = data.get('product_id')
    date_str = datetime.now().isoformat()
    
    if not name or not phone or not product_id:
        return jsonify({"success": False, "message": "Thiếu thông tin"})
        
    db = get_db()
    # Tìm hoặc tạo Customer
    cust = db.execute('SELECT id FROM customers WHERE phone_number = ?', (phone,)).fetchone()
    if cust:
        customer_id = cust['id']
    else:
        cursor = db.execute('INSERT INTO customers (name, phone_number, zalo, registration_date) VALUES (?, ?, ?, ?)', 
                            (name, phone, phone, date_str))
        customer_id = cursor.lastrowid
        
    # Lấy giá trị tiền
    prod = db.execute('SELECT price FROM products WHERE id = ?', (product_id,)).fetchone()
    if not prod:
        return jsonify({"success": False, "message": "Sản phẩm không hợp lệ"})
    amount = prod['price']
    
    # Tạo Order Pending
    cursor = db.execute('INSERT INTO orders (customer_id, product_id, amount, status, order_date) VALUES (?, ?, ?, ?, ?)',
               (customer_id, product_id, amount, 'pending', date_str))
    db.commit()
    order_id = cursor.lastrowid
    
    desc = f"PETDA{order_id}"
    
    return jsonify({
        "success": True, 
        "order_id": order_id, 
        "amount": amount, 
        "description": desc
    })

@app.route('/api/check_order/<int:id>', methods=['GET'])
def check_order(id):
    db = get_db()
    order = db.execute('SELECT status FROM orders WHERE id = ?', (id,)).fetchone()
    if order:
        return jsonify({"success": True, "status": order['status']})
    return jsonify({"success": False})

@app.route('/api/webhook/sepay', methods=['POST'])
def webhook_sepay():
    # SePay Webhook payload thường chứa nội dung CK trong trường 'content' hoặc 'transaction_content'
    payload = request.json or {}
    payload_str = str(payload).upper()
    
    db = get_db()
    # Tìm tất cả đơn Pending
    pending_orders = db.execute("SELECT id FROM orders WHERE status = 'pending'").fetchall()
    
    for order in pending_orders:
        desc = f"PETDA{order['id']}"
        # Khớp nội dung description trong JSON của Sepay với đơn hàng
        if desc in payload_str:
            db.execute("UPDATE orders SET status = 'success', payment_method = 'auto' WHERE id = ?", (order['id'],))
            db.commit()
            print(f">>> WEBHOOK: Đã nhận tiền và cập nhật đơn {order['id']}")
            return jsonify({"success": True, "message": "Ghi nhận thành công"})
            
    print(">>> WEBHOOK: Không khớp đơn hàng pending nào. Nội dung:", payload_str)
    return jsonify({"success": True, "message": "Ignored"})

if __name__ == '__main__':
    # Hỗ trợ nhận webhook mọi IP khi dùng ngrok
    app.run(debug=True, port=3000, host='0.0.0.0')
