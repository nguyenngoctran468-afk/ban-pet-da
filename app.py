from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
from datetime import datetime
import requests
import os
import resend
import threading
import time

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
# CẤU HÌNH RESEND EMAIL
# ==========================================
def load_resend_key():
    # Ưu tiên lấy từ Biến môi trường (Environment Variable) trên Render
    key = os.environ.get('RESEND_API_KEY')
    if key:
        return key.strip()
    # Nếu không có thì mới đọc từ file
    try:
        with open('resend_config.txt', 'r') as f:
            return f.read().strip()
    except:
        return None

resend.api_key = load_resend_key()

def send_email(to_email, subject, html_content):
    if not resend.api_key:
        resend.api_key = load_resend_key() # Thử load lại
        if not resend.api_key:
            print(">>> LỖI: Chưa cấu hình Resend API Key (Kiểm tra Environment Variables trên Render)")
            return False
    try:
        params = {
            "from": "onboarding@resend.dev",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        resend.Emails.send(params)
        print(f">>> [SUCCESS] Đã gửi email tới: {to_email}")
        return True
    except Exception as e:
        error_msg = str(e)
        print(f">>> [ERROR] Gửi email thất bại tới {to_email}: {error_msg}")
        if "restricted" in error_msg.lower() or "forbidden" in error_msg.lower():
            print(">>> LƯU Ý: Resend Free chỉ cho phép gửi tới email đăng ký của bạn. Hãy verify domain để gửi cho khách lạ.")
        return False

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
    
    # Kiểm tra trạng thái API Key để báo cho Admin
    resend_stat = "Đã cấu hình ✅" if resend.api_key else "Chưa cấu hình ❌"
    
    return render_template('admin.html', tab=tab, products=products, customers=customers, orders=orders, resend_stat=resend_stat)

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
        "email": request.form.get('email', ''),
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
    
    # Trừ kho NẾU tạo đơn thành công
    if data['status'] == 'success':
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
        
        # Xử lý kho theo logic: Chỉ 'success' mới bị trừ kho
        prod = supabase_get('products', f'id=eq.{product_id}')
        if prod and isinstance(prod, list) and len(prod) > 0:
            current_stock = int(prod[0].get('stock', 0))
            if status == 'success' and old_status != 'success':
                supabase_update('products', 'id', product_id, {"stock": current_stock - 1})
            elif status != 'success' and old_status == 'success':
                supabase_update('products', 'id', product_id, {"stock": current_stock + 1})
                
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
    email = data.get('email')
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
            "name": name, "phone_number": phone, "email": email, "zalo": phone, "registration_date": date_str
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
                
                # Trừ kho cập nhật
                prod = supabase_get('products', f"id=eq.{order['product_id']}")
                if prod and isinstance(prod, list) and len(prod) > 0:
                    current_stock = int(prod[0].get('stock', 0))
                    supabase_update('products', 'id', order['product_id'], {"stock": current_stock - 1})
                
                print(f">>> WEBHOOK: Đã nhận tiền và cập nhật đơn {order['id']}")
                return jsonify({"success": True, "message": "Ghi nhận thành công"})
                
    print(">>> WEBHOOK: Không khớp đơn hàng pending nào. Nội dung:", payload_str)
    return jsonify({"success": True, "message": "Ignored"})

@app.route('/admin/resend-test')
def admin_resend_test():
    test_email = "nguyenngoctran468@gmail.com" # Email chính chủ của bạn
    subject = "🔔 TEST KẾT NỐI RESEND"
    content = "<p>Nếu bạn thấy thư này, nghĩa là hệ thống đã kết nối Resend thành công!</p>"
    
    success = send_email(test_email, subject, content)
    if success:
        return f"<h3>Thành công! Hãy kiểm tra hộp thư {test_email}</h3><a href='/admin?tab=customers'>Quay lại Admin</a>"
    else:
        return f"<h3>Thất bại! Có lỗi xảy ra. Hãy kiểm tra Logs trên Render hoặc Environment Variables.</h3><p>Đã thử gửi tới: {test_email}</p><a href='/admin?tab=customers'>Quay lại Admin</a>"

# ==========================================
# EMAIL SEQUENCE LOGIC
# ==========================================
EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "🎉 Chào mừng bạn gia nhập Hội Những Người Nuôi Đá Vô Tri!",
        "content": """
        <p>Chào bạn, chủ nhân tương lai!</p>
        <p>Bạn vừa chính thức đặt một chân vào thế giới của sự tĩnh lặng tuyệt đối (mình nói thiệt á, nó hông kêu, hông sủa, hông đòi ăn, hông làm gì hết).</p>
        <p>Cảm ơn bạn đã tin tưởng mình và "bé đá" tương lai. Trong vài ngày tới, mình sẽ kể cho bạn nghe tại sao hàng ngàn Gen Z lại chọn nuôi đá để giải nghiệp chốn công sở nhé.</p>
        <p>Đừng quên kiểm tra inbox thường xuyên, mình có chuẩn bị vài điều "vô tri nhưng hữu ích" dành riêng cho bạn đó.</p>
        <br>
        <p>Thân ái,<br><b>Team Pet Đá</b></p>
        """
    },
    "nurture": {
        "subject": "🧘 Bí kíp 'Tịnh Tâm' 0đ ngay tại bàn làm việc",
        "content": """
        <p>Chào bạn,</p>
        <p>Bạn đã bao giờ định chửi sếp nhưng rồi lại phải nuốt cục tức vào trong chưa? Hay bị dí deadline đến mức muốn hóa đá luôn cho rồi?</p>
        <p>Bí quyết của những "con sen" hệ đá chính là: <b>Lôi bé đá ra chửi thẳng mặt.</b></p>
        <p>Nó sẽ im lặng chịu trận 24/7, hông bao giờ mách lẻo, hông bao giờ phán xét. Đó là sự trị liệu tâm lý đỉnh cao mà không có con mèo hay con chó nào làm được.</p>
        <p>Chỉ cần ngồi im lặng cùng nó 2 phút mỗi khi stress, bạn sẽ thấy deadline cũng chỉ là những hạt cát thôi.</p>
        <br>
        <p>Chúc bạn một ngày làm việc bớt nghiệp,<br><b>Team Pet Đá</b></p>
        """
    },
    "sales": {
        "subject": "🪨 Cơ hội đón 'Bé Đá Cưng' về dinh (Lô này chỉ còn vài bé!)",
        "content": """
        <p>Chào bạn,</p>
        <p>Lô đá 'lỳ lợm' đợt này của mình đang vơi dần rồi, hiện tại chỉ còn vài bé Đá Cưng (79k) chờ được bế về thôi.</p>
        <p>Tại sao bạn nên chốt ngay?</p>
        <ul>
            <li><b>Độc bản:</b> Mỗi bé là một vibe khác nhau.</li>
            <li><b>An toàn:</b> Đóng gói cực sang chảnh, ship tới văn phòng ai cũng tưởng đồ hiệu.</li>
            <li><b>Giá rẻ:</b> Chỉ bằng 2 ly trà đào, mà mua được một 'người lắng nghe' tận tụy cả đời.</li>
        </ul>
        <p>👉 <b><a href='https://ban-pet-da.onrender.com/checkout'>ĐẶT HÀNG TẠI ĐÂY</a></b></p>
        <br>
        <p>Hẹn gặp bạn và bé đá của bạn,<br><b>Team Pet Đá</b></p>
        """
    }
}

def trigger_email_sequence(email, name):
    is_test = "+test" in email.lower()
    
    # Email 1: Welcome
    send_email(email, EMAIL_TEMPLATES["welcome"]["subject"], EMAIL_TEMPLATES["welcome"]["content"])
    
    if is_test:
        # Gửi luôn 2 email còn lại ngay lập tức
        print(f">>> TEST MODE: Gửi toàn bộ sequence cho {email}")
        send_email(email, EMAIL_TEMPLATES["nurture"]["subject"], EMAIL_TEMPLATES["nurture"]["content"])
        send_email(email, EMAIL_TEMPLATES["sales"]["subject"], EMAIL_TEMPLATES["sales"]["content"])
    else:
        # Lên lịch gửi (Dùng Threading đơn giản cho bài tập này)
        def delayed_nurture():
            time.sleep(172800) # 2 ngày
            send_email(email, EMAIL_TEMPLATES["nurture"]["subject"], EMAIL_TEMPLATES["nurture"]["content"])
            time.sleep(86400) # 1 ngày sau đó
            send_email(email, EMAIL_TEMPLATES["sales"]["subject"], EMAIL_TEMPLATES["sales"]["content"])
            
        threading.Thread(target=delayed_nurture).start()

@app.route('/api/waitlist', methods=['POST'])
def api_waitlist():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    zalo = data.get('zalo')
    
    if not phone or not email:
        return jsonify({"success": False, "message": "Thiếu thông tin"})
        
    date_str = datetime.now().isoformat()
    cust = supabase_get('customers', f'phone_number=eq.{phone}')
    
    if not cust or len(cust) == 0:
        supabase_insert('customers', {
            "name": name, "phone_number": phone, "email": email, "zalo": zalo, "registration_date": date_str
        })
    
    # KÍCH HOẠT SEQUENCE TRONG MỌI TRƯỜNG HỢP KHI ĐIỀN FORM (ĐỂ TEST)
    trigger_email_sequence(email, name)
    return jsonify({"success": True, "message": "Đã ghi nhận và kích hoạt chuỗi email"})

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
