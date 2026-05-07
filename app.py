from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
from datetime import datetime
import requests
import os
import resend
import threading
import time
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ==========================================
# CẤU HÌNH SUPABASE ONLINE
# Đọc từ Environment Variable (VPS/Render) trước — không hardcode secrets!
# ==========================================
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

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
resend.api_key = os.environ.get('RESEND_API_KEY')

def send_email(to_email, subject, html_content):
    if not resend.api_key:
        resend.api_key = os.environ.get('RESEND_API_KEY') # Thử load lại
        if not resend.api_key:
            print(">>> LỖI: Chưa cấu hình Resend API Key (Kiểm tra Environment Variables trên Render)")
            return False
    try:
        # FIX LỖI SANDBOX: Nếu gửi tới email có dấu +, Resend Free có thể chặn.
        # Ta sẽ gửi tới email gốc nếu là chế độ test để Resend cho phép.
        final_to = to_email
        if "onboarding@resend.dev" in "onboarding@resend.dev" and "+" in to_email:
             # Nếu là email gmail có dấu +, ta lấy phần trước dấu + và phần sau dấu @
             parts = to_email.split('@')
             if '+' in parts[0]:
                 final_to = parts[0].split('+')[0] + '@' + parts[1]

        params = {
            "from": "onboarding@resend.dev",
            "to": [final_to],
            "subject": subject,
            "html": html_content,
        }
        resend.Emails.send(params)
        print(f">>> [SUCCESS] Đã gửi email tới: {final_to} (Gốc: {to_email})")
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

@app.route('/api/products')
def api_products():
    products = supabase_get('products', 'order=id.asc')
    return jsonify(products)

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

    # GỬI EMAIL XÁC NHẬN ĐƠN HÀNG (BƯỚC 6 TRONG SOP)
    # Lấy thông tin khách hàng để lấy email
    cust = supabase_get('customers', f"id=eq.{data['customer_id']}")
    if cust and len(cust) > 0:
        target_email = cust[0].get('email')
        if target_email:
            subject = f"🛒 Ê, chốt đơn thành công rồi nha! Đợi Bé Đá tới 'giải nghiệp' cho bạn nè"
            prod_name = supabase_get('products', f"id=eq.{product_id}")[0].get('name') if product_id else 'Sản phẩm Pet Đá'
            amount_formatted = "{:,.0f}".format(float(data['amount']))
            status_text = "Đã thanh toán ✅" if data['status'] == 'success' else "Chờ thanh toán ⏳"
            
            content = f"""
            <div style="font-family: sans-serif; line-height: 1.6; color: #333;">
                <h3>Chào {cust[0].get('name')},</h3>
                <p>Nghe đồn bạn vừa quyết định đón một bé <b>{prod_name}</b> về đúng không? Chúc mừng bạn nha, từ nay bàn làm việc của bạn sẽ có một thành viên mới "ngoan" nhất thế giới: Bao chửi, bao ngồi im, bao nghe than vãn mà không bao giờ mách lẻo với sếp.</p>
                
                <div style="background: #f4f7f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><b>Thông tin đơn của bạn nè:</b></p>
                    <ul style="list-style: none; padding: 0;">
                        <li>📦 <b>Sản phẩm:</b> {prod_name}</li>
                        <li>💰 <b>Tổng thiệt hại:</b> {amount_formatted}đ</li>
                        <li>⚡ <b>Trạng thái:</b> {status_text}</li>
                    </ul>
                </div>

                <p><b>🚚 Hướng dẫn nhận hàng:</b></p>
                <p>Bé đá đang được mình "tắm rửa" sạch sẽ, đóng gói cực kỳ cẩn thận vào hộp xịn, đính thêm cả Giấy Khai Sinh viết tay nữa. Bạn chỉ cần giữ điện thoại, khi nào shipper bốc máy gọi thì bay ra nhận là xong. Nhớ lúc khui hộp phải nhẹ tay kẻo ẻm giật mình nha!</p>
                
                <p>Cảm ơn bạn đã ủng hộ một khởi nghiệp vô tri như mình. Hy vọng bé đá sẽ giúp bạn "tịnh tâm" bước qua mùa deadline này.</p>
                
                <br>
                <p>Thân ái (và quyết thắng deadline),<br>
                <b>Team Pet Đá</b></p>
            </div>
            """
            send_email(target_email, subject, content)
        
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
                
                # GIAO HÀNG TỰ ĐỘNG NẾU LÀ EBOOK (ID: 3)
                if int(product_id) == 3:
                    customer = supabase_get('customers', f"id=eq.{order[0].get('customer_id')}")
                    if customer and len(customer) > 0:
                        target_email = customer[0].get('email')
                        if target_email:
                            email_content = EMAIL_TEMPLATES["ebook_delivery"]["content"].format(
                                order_id=id, 
                                email=target_email
                            )
                            send_email(target_email, EMAIL_TEMPLATES["ebook_delivery"]["subject"], email_content)
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
        # CẬP NHẬT thông tin mới nhất cho khách hàng cũ (để tránh trường hợp tên bị cũ khi test)
        supabase_update('customers', 'id', customer_id, {
            "name": name, 
            "email": email,
            "zalo": phone # Cập nhật luôn zalo theo số mới
        })
    else:
        # Tạo KH mới
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
    # Thêm Cache-Control để trình duyệt không lưu phản hồi cũ
    order = supabase_get('orders', f'id=eq.{id}')
    
    response_data = {"success": False}
    if order and len(order) > 0:
        status = order[0].get('status')
        print(f">>> [CHECK ORDER] Đơn #{id} hiện tại: {status}")
        response_data = {"success": True, "status": status}
    
    res = jsonify(response_data)
    res.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    res.headers['Pragma'] = 'no-cache'
    res.headers['Expires'] = '0'
    return res

@app.route('/api/webhook/sepay', methods=['POST'])
def webhook_sepay():
    payload = request.json or {}
    print(f"\n>>> [SEPAY WEBHOOK] Nhận dữ liệu: {payload}")
    
    # Chuyển payload sang chuỗi hoa để tìm kiếm linh hoạt
    payload_str = str(payload).upper()
    
    # Tìm mã PETDA{id} - Ưu tiên tìm pattern PETDA + Số
    match = re.search(r'PETDA(\d+)', payload_str)
    
    if match:
        order_id = int(match.group(1))
        print(f">>> [SEPAY WEBHOOK] Phát hiện mã đơn hàng: {order_id}")
        
        # Kiểm tra đơn hàng này trong DB
        order = supabase_get('orders', f'id=eq.{order_id}')
        if order and isinstance(order, list) and len(order) > 0:
            order_data = order[0]
            
            if order_data.get('status') == 'pending':
                # CẬP NHẬT TRẠNG THÁI SUCCESS
                supabase_update('orders', 'id', order_id, {"status": "success", "payment_method": "auto"})
                
                # Trừ kho
                product_id = int(order_data.get('product_id'))
                prod = supabase_get('products', f"id=eq.{product_id}")
                if prod and isinstance(prod, list) and len(prod) > 0:
                    current_stock = int(prod[0].get('stock', 0))
                    supabase_update('products', 'id', product_id, {"stock": current_stock - 1})
                
                # GIAO HÀNG TỰ ĐỘNG NẾU LÀ SẢN PHẨM SỐ (ID: 3)
                if product_id == 3:
                    customer = supabase_get('customers', f"id=eq.{order_data.get('customer_id')}")
                    if customer and len(customer) > 0:
                        target_email = customer[0].get('email')
                        if target_email:
                            email_content = EMAIL_TEMPLATES["ebook_delivery"]["content"].format(
                                order_id=order_id, 
                                email=target_email
                            )
                            send_email(target_email, EMAIL_TEMPLATES["ebook_delivery"]["subject"], email_content)
                            print(f">>> [DIGITAL DELIVERY] Đã gửi Ebook tới {target_email}")

                print(f">>> [SEPAY WEBHOOK] CHÚC MỪNG: Đơn {order_id} đã thanh toán thành công!")
                return jsonify({"success": True, "message": f"Order {order_id} updated to success"})
            else:
                print(f">>> [SEPAY WEBHOOK] Bỏ qua: Đơn {order_id} đã ở trạng thái {order_data.get('status')}")
                return jsonify({"success": True, "message": "Already processed"})
        else:
            print(f">>> [SEPAY WEBHOOK] LỖI: Không tìm thấy đơn {order_id} trong database.")
    else:
        print(">>> [SEPAY WEBHOOK] Không tìm thấy mã PETDA trong nội dung chuyển khoản.")
        
    return jsonify({"success": True, "message": "Ignored"})

@app.route('/admin/resend-test')
def admin_resend_test():
    test_email = "nguyenngoctran468@gmail.com" # Email chính chủ
    
    # Test mẫu email giao Ebook mới
    email_content = EMAIL_TEMPLATES["ebook_delivery"]["content"].format(
        order_id="TEST_123", 
        email=test_email
    )
    success = send_email(test_email, EMAIL_TEMPLATES["ebook_delivery"]["subject"], email_content)
    
    if success:
        return f"<h3>Thành công! Đã gửi Email Giao Ebook tới {test_email}</h3><p>Vui lòng kiểm tra hòm thư của bạn.</p><a href='/admin?tab=orders'>Quay lại Admin</a>"
    else:
        return f"<h3>Lỗi gửi mail!</h3><p>Hãy kiểm tra Logs hoặc API Key trong .env.</p><a href='/admin?tab=orders'>Quay lại Admin</a>"

# ------------- SẢN PHẨM SỐ (EBOOK) -------------
@app.route('/san-pham/<slug>')
def product_landing(slug):
    if slug != 'ai-affiliate-blueprint':
        return "Sản phẩm không tồn tại", 404
    product = supabase_get('products', 'id=eq.3')
    prod_data = product[0] if product else {"price": 397000}
    return render_template('ebook_landing.html', slug=slug, product=prod_data)

@app.route('/san-pham/<slug>/checkout')
def product_checkout(slug):
    if slug != 'ai-affiliate-blueprint':
        return "Sản phẩm không tồn tại", 404
    product = supabase_get('products', 'id=eq.3')
    if not product:
        return "Lỗi lấy sản phẩm", 500
    return render_template('ebook_checkout.html', slug=slug, product=product[0])

@app.route('/san-pham/<slug>/cam-on')
def product_thankyou(slug):
    order_id = request.args.get('order_id')
    email = request.args.get('email')
    return render_template('ebook_cam_on.html', slug=slug, order_id=order_id, email=email)

@app.route('/api/download/ebook')
def download_ebook():
    order_id = request.args.get('order_id')
    email = request.args.get('email')
    
    if not order_id or not email:
        return "Thiếu thông tin xác thực", 400
        
    order = supabase_get('orders', f'id=eq.{order_id}')
    if not order or len(order) == 0:
        return "Đơn hàng không tồn tại", 404
        
    if order[0].get('status') != 'success':
        return "Đơn hàng chưa được thanh toán", 403
        
    customer = supabase_get('customers', f"id=eq.{order[0].get('customer_id')}")
    if not customer or customer[0].get('email') != email:
        return "Email không khớp với đơn hàng", 403
        
    products_dir = os.path.join(app.root_path, 'products')
    return send_from_directory(products_dir, 'ai_affiliate_blueprint.pdf', as_attachment=True)

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
    },
    "ebook_delivery": {
        "subject": "🔥 [DOWNLOAD] Bản thiết kế AI Affiliate Blueprint của bạn đây!",
        "content": """
        <div style="font-family: sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #6366f1;">Chúc mừng bạn đã sở hữu AI Affiliate Blueprint!</h2>
            <p>Chào bạn, tấm vé thông hành vào thị trường TikTok US đã nằm trong tay bạn. Đây là bước ngoặt để bạn bắt đầu kiếm thu nhập bằng USD với sự trợ giúp của AI.</p>
            
            <div style="background: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; margin: 20px 0;">
                <h3 style="margin-top: 0;">📦 Link Tải Tài Liệu:</h3>
                <p>Bạn có thể tải về máy trực tiếp tại đây (link có hiệu lực vĩnh viễn):</p>
                <a href="https://phaodr.com/api/download/ebook?order_id={order_id}&email={email}" style="display: inline-block; padding: 12px 24px; background: #6366f1; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">TẢI EBOOK (.PDF)</a>
            </div>

            <h3>🎁 Quà tặng kèm theo (Bonus):</h3>
            <ul>
                <li><b>Checklist 20 lỗi bay nick:</b> Đã đính kèm trong Ebook.</li>
                <li><b>Top 10 sản phẩm Supplement:</b> Xem tại Chương 6.</li>
                <li><b>Bộ Prompt AI độc quyền:</b> Xem tại Chương 4.</li>
            </ul>

            <p>Nếu gặp khó khăn trong quá trình tải file hoặc setup, hãy nhắn tin ngay cho Support trong nhóm Zalo nhé.</p>
            <p>Hẹn gặp bạn ở vạch đích!</p>
            <br>
            <p>Thân ái,<br><b>Team AI Affiliate</b></p>
        </div>
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
        # Nếu chưa có khách -> Thêm mới
        supabase_insert('customers', {
            "name": name, "phone_number": phone, "email": email, "zalo": zalo, "registration_date": date_str
        })
        msg = "Đã thêm khách hàng mới và kích hoạt chuỗi email"
    else:
        # Nếu đã có -> Cập nhật email và tên mới nhất (để bạn thấy update trong Admin)
        customer_id = cust[0]['id']
        supabase_update('customers', 'id', customer_id, {"email": email, "name": name})
        msg = "Đã cập nhật thông tin khách hàng và kích hoạt lại chuỗi email"
    
    # KÍCH HOẠT SEQUENCE TRONG MỌI TRƯỜNG HỢP KHI ĐIỀN FORM (ĐỂ TEST)
    trigger_email_sequence(email, name)
    return jsonify({"success": True, "message": msg})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(debug=True, port=port, host='0.0.0.0')
