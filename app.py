from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
from datetime import datetime
import requests
import os

app = Flask(__name__)
CORS(app)

# ==========================================
# CẤU HÌNH SUPABASE ONLINE
# ==========================================
SUPABASE_URL = "https://aahbbepwytfpuzjuxocv.supabase.co"
SUPABASE_KEY = "sb_publishable_WLySCRyt5XwNVFeKC7XoVw_3JQGb9kg"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def supabase_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params:
        url += f"?{params}"
    else:
        url += "?select=*"
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []

def supabase_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    res = requests.post(url, headers=headers, json=data)
    return res.json() if res.status_code in [200, 201] else []

def supabase_update(table, match_col, match_val, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{match_col}=eq.{match_val}"
    res = requests.patch(url, headers=headers, json=data)
    return res.json() if res.status_code in [200, 204] else []

def supabase_delete(table, match_col, match_val):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{match_col}=eq.{match_val}"
    requests.delete(url, headers=headers)

# ==========================================
# ROUTES CƠ BẢN
# ==========================================
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/admin')
def admin():
    tab = request.args.get('tab', 'products')
    
    products = supabase_get('products', 'order=id.desc')
    customers = supabase_get('customers', 'order=id.desc')
    
    # Query orders và kèm theo thông tin bảng liên kết
    raw_orders = supabase_get('orders', 'select=*,customers(name),products(name)&order=id.desc')
    
    # Chuẩn hoá data để phù hợp với hiển thị HTML cũ (orders.customer_name, orders.product_name)
    orders = []
    if isinstance(raw_orders, list):
        for o in raw_orders:
            o['customer_name'] = o.get('customers', {}).get('name', '') if o.get('customers') else 'Chưa rõ'
            o['product_name'] = o.get('products', {}).get('name', '') if o.get('products') else 'Chưa rõ'
            orders.append(o)
    
    return render_template('admin.html', tab=tab, products=products, customers=customers, orders=orders)

# ------------- PRODUCTS -------------
@app.route('/admin/product/add', methods=['POST'])
def add_product():
    data = {
        "name": request.form['name'],
        "price": float(request.form['price']),
        "description": request.form['description'],
        "stock": int(request.form['stock'])
    }
    supabase_insert('products', data)
    return redirect(url_for('admin', tab='products'))

@app.route('/admin/product/delete/<int:id>')
def delete_product(id):
    supabase_delete('products', 'id', id)
    return redirect(url_for('admin', tab='products'))

# ------------- CUSTOMERS -------------
@app.route('/admin/customer/add', methods=['POST'])
def add_customer():
    data = {
        "name": request.form['name'],
        "phone_number": request.form['phone'],
        "zalo": request.form['zalo'],
        "registration_date": request.form['date']
    }
    supabase_insert('customers', data)
    return redirect(url_for('admin', tab='customers'))

@app.route('/admin/customer/delete/<int:id>')
def delete_customer(id):
    supabase_delete('customers', 'id', id)
    return redirect(url_for('admin', tab='customers'))

# ------------- ORDERS -------------
@app.route('/admin/order/add', methods=['POST'])
def add_order():
    if not request.form.get('customer_id') or not request.form.get('product_id'):
        return redirect(url_for('admin', tab='orders'))
        
    product_id = request.form['product_id']
    data = {
        "customer_id": request.form['customer_id'],
        "product_id": product_id,
        "amount": float(request.form['amount']),
        "status": request.form['status'],
        "payment_method": 'manual',
        "order_date": request.form['order_date']
    }
    supabase_insert('orders', data)
    
    # Trừ kho
    prod = supabase_get('products', f'id=eq.{product_id}')
    if prod and isinstance(prod, list) and len(prod) > 0:
        current_stock = int(prod[0].get('stock', 0))
        supabase_update('products', 'id', product_id, {"stock": current_stock - 1})
        
    return redirect(url_for('admin', tab='orders'))

@app.route('/admin/order/update/<int:id>', methods=['POST'])
def update_order(id):
    status = request.form.get('status')
    if status in ['success', 'cancelled', 'pending']:
        order = supabase_get('orders', f'id=eq.{id}')
        if not order or not isinstance(order, list) or len(order) == 0:
            return redirect(url_for('admin', tab='orders'))
            
        old_status = order[0].get('status')
        product_id = order[0].get('product_id')
        
        supabase_update('orders', 'id', id, {"status": status, "payment_method": "manual"})
        
        # Xử lý kho khi huỷ / đổi từ trạng thái huỷ lại bình thường
        prod = supabase_get('products', f'id=eq.{product_id}')
        if prod and isinstance(prod, list) and len(prod) > 0:
            current_stock = int(prod[0].get('stock', 0))
            if status == 'cancelled' and old_status != 'cancelled':
                supabase_update('products', 'id', product_id, {"stock": current_stock + 1})
            if status != 'cancelled' and old_status == 'cancelled':
                supabase_update('products', 'id', product_id, {"stock": current_stock - 1})
                
    return redirect(url_for('admin', tab='orders'))

@app.route('/admin/order/delete/<int:id>')
def delete_order(id):
    supabase_delete('orders', 'id', id)
    return redirect(url_for('admin', tab='orders'))

# ------------- CHECKOUT FLOW -------------
@app.route('/checkout')
@app.route('/thanh-toan')
def checkout():
    products = supabase_get('products', 'order=id.desc')
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
        
    # Tìm KH
    cust = supabase_get('customers', f'phone_number=eq.{phone}')
    if cust and isinstance(cust, list) and len(cust) > 0:
        customer_id = cust[0]['id']
    else:
        # Tạo KH
        new_cust = supabase_insert('customers', {
            "name": name, "phone_number": phone, "zalo": phone, "registration_date": date_str
        })
        if new_cust and len(new_cust) > 0:
            customer_id = new_cust[0]['id']
        else:
            return jsonify({"success": False, "message": "Lỗi tạo khách hàng"})
            
    # Tìm SP
    prod = supabase_get('products', f'id=eq.{product_id}')
    if not prod or len(prod) == 0:
        return jsonify({"success": False, "message": "Sản phẩm không hợp lệ"})
    amount = prod[0]['price']
    
    # Tạo Đơn
    new_order = supabase_insert('orders', {
        "customer_id": customer_id, "product_id": product_id, "amount": amount,
        "status": "pending", "payment_method": "auto", "order_date": date_str
    })
    
    if new_order and len(new_order) > 0:
        order_id = new_order[0]['id']
        desc = f"PETDA{order_id}"
        return jsonify({"success": True, "order_id": order_id, "amount": amount, "description": desc})
        
    return jsonify({"success": False, "message": "Lỗi lưu kho"})

@app.route('/api/check_order/<int:id>', methods=['GET'])
def check_order(id):
    order = supabase_get('orders', f'id=eq.{id}')
    if order and len(order) > 0:
        return jsonify({"success": True, "status": order[0].get('status')})
    return jsonify({"success": False})

@app.route('/api/webhook/sepay', methods=['POST'])
def webhook_sepay():
    payload = request.json or {}
    payload_str = str(payload).upper()
    
    pending_orders = supabase_get('orders', 'status=eq.pending')
    if isinstance(pending_orders, list):
        for order in pending_orders:
            desc = f"PETDA{order['id']}"
            if desc in payload_str:
                supabase_update('orders', 'id', order['id'], {"status": "success", "payment_method": "auto"})
                print(f">>> WEBHOOK: Đã nhận tiền và cập nhật đơn {order['id']}")
                return jsonify({"success": True, "message": "Ghi nhận thành công"})
                
    print(">>> WEBHOOK: Không khớp đơn hàng pending nào. Nội dung:", payload_str)
    return jsonify({"success": True, "message": "Ignored"})

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
