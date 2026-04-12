import sqlite3

# Kết nối database
conn = sqlite3.connect('brain.db')
conn.row_factory = sqlite3.Row
db = conn.cursor()

products = db.execute('SELECT * FROM products').fetchall()
customers = db.execute('SELECT * FROM customers').fetchall()
orders = db.execute('''
    SELECT orders.*, customers.name as customer_name, products.name as product_name 
    FROM orders 
    LEFT JOIN customers ON orders.customer_id = customers.id 
    LEFT JOIN products ON orders.product_id = products.id
    ORDER BY orders.id DESC
''').fetchall()

# ------ 1. TẠO thanh-toan.html ------
thanh_toan_html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thanh Toán - Pet Đá</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #f0f7f4; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .checkout-box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; border: 2px dashed #f97316; max-width: 400px; }
        h1 { color: #1f2937; margin-top: 0; font-size: 1.5rem; }
        p { color: #4b5563; }
        img { border-radius: 8px; margin: 20px 0; max-width: 100%; border: 1px solid #e5e7eb; }
    </style>
</head>
<body>
    <div class="checkout-box">
        <h1>Thanh toán tự động SePay</h1>
        <p>Quét mã QR bằng App ngân hàng. Số tiền <strong>2.000đ</strong> và nội dung sẽ tự động điền.</p>
        <img src="https://qr.sepay.vn/img?acc=10003821008&bank=TPBank&amount=2000&des=TEST" alt="QR Thanh Toán Sepay">
        <p style="color: #ef4444; font-weight: bold;">Kiểm tra kỹ tên chủ khoản trước khi chuyển nhé!</p>
        <a href="/" style="display:inline-block; margin-top:20px; text-decoration:none; color: #3b82f6; font-weight: bold;">← Quay lại trang chủ</a>
    </div>
</body>
</html>
"""
with open('thanh-toan.html', 'w', encoding='utf-8') as f:
    f.write(thanh_toan_html)

# ------ 2. TẠO admin.html ------
# Hàm hỗ trợ sinh code HTML cho các bảng
def render_products(prods):
    res = ""
    for p in prods:
        status_color = "#def7ec" if p['stock'] > 0 else "#fde8e8"
        text_color = "#03543f" if p['stock'] > 0 else "#9b1c1c"
        res += f"<tr><td>{p['name']}</td><td>{p['price']:,.0f}đ</td><td>{p['description']}</td>"
        res += f"<td><span style='background: {status_color}; color: {text_color}; padding: 4px 8px; border-radius: 12px; font-weight: bold;'>{p['stock']}</span></td>"
        res += "<td><button class='btn' disabled>Xóa (Demo)</button></td></tr>"
    return res if res else "<tr><td colspan='5' style='text-align:center; padding: 20px;'>Chưa có sản phẩm.</td></tr>"

def render_customers(custs):
    res = ""
    for c in custs:
        date_str = c['registration_date'].split('T')[0] if 'T' in c['registration_date'] else c['registration_date']
        res += f"<tr><td>#{c['id']}</td><td>{c['name']}</td><td>{c['phone_number']}</td><td>{c['zalo']}</td><td>{date_str}</td>"
        res += "<td><button class='btn' disabled>Xóa (Demo)</button></td></tr>"
    return res if res else "<tr><td colspan='6' style='text-align:center; padding: 20px;'>Chưa có khách hàng.</td></tr>"

def render_orders(ords):
    res = ""
    for o in ords:
        status_bg = "#def7ec" if "thanh toán" in o['status'] or "giao" in o['status'] else "#fef3c7"
        status_color = "#03543f" if "thanh toán" in o['status'] or "giao" in o['status'] else "#92400e"
        res += f"<tr><td>{o['customer_name']}</td><td>{o['product_name']}</td><td style='color:#10b981; font-weight:bold;'>{o['amount']:,.0f}đ</td><td>{o['order_date']}</td>"
        res += f"<td><span class='status-badge' style='background:{status_bg}; color:{status_color};'>{o['status']}</span></td>"
        res += "<td><button class='btn' disabled>Xóa (Demo)</button></td></tr>"
    return res if res else "<tr><td colspan='6' style='text-align:center; padding: 20px;'>Chưa có đơn hàng. (Hãy tạo từ Local server)</td></tr>"

admin_html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Admin Panel - Xem Trước (Static)</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 0; background-color: #f4f7f6; }}
        .sidebar {{ width: 220px; background: #2c3e50; color: white; position: fixed; height: 100%; padding-top: 20px; }}
        .sidebar h3 {{ text-align: center; margin-bottom: 30px; }}
        .sidebar a {{ display: block; padding: 15px 20px; color: #ecf0f1; text-decoration: none; cursor: pointer; }}
        .sidebar a:hover, .sidebar a.active {{ background: #34495e; border-left: 4px solid #3498db; }}
        .content {{ margin-left: 220px; padding: 30px; }}
        .tab-pane {{ display: none; }}
        .tab-pane.active {{ display: block; }}
        table {{ width: 100%; border-collapse: collapse; background: white; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 15px; border-bottom: 1px solid #edf2f7; text-align: left; }}
        th {{ background: #f8fafc; font-weight: 600; text-transform: uppercase; font-size: 0.85rem; }}
        .btn {{ padding: 6px 12px; background: #e74c3c; color: white; border-radius: 4px; border: none; font-size: 0.85rem; opacity: 0.5; }}
        .warning-banner {{ background: #fffbeb; color: #b45309; padding: 15px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #fde68a; }}
        .status-badge {{ padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>⚡ CRM ADMIN</h3>
        <a id="nav-products" class="active" onclick="switchTab('products')">📦 Sản Phẩm</a>
        <a id="nav-customers" onclick="switchTab('customers')">👥 Khách Hàng (Đã import)</a>
        <a id="nav-orders" onclick="switchTab('orders')">🛒 Đơn Hàng</a>
    </div>

    <div class="content">
        <div class="warning-banner">
            <strong>Chế độ Xem Trước (Static View):</strong> Giao diện này được xuất tự động từ Database để người đánh giá (Reviewer) có thể xem data thật trên link public. Để thêm/sửa/xoá, tài khoản Admin cục bộ phải chạy trên http://127.0.0.1:3000.
        </div>

        <div id="tab-products" class="tab-pane active">
            <h2 style="margin-top:0;">Quản lý Sản Phẩm</h2>
            <table>
                <tr><th>Tên Sản Phẩm</th><th>Giá</th><th>Mô tả</th><th>Tồn kho</th><th>Hành động</th></tr>
                {render_products(products)}
            </table>
        </div>

        <div id="tab-customers" class="tab-pane">
            <h2 style="margin-top:0;">Danh sách Khách Tự Động Load</h2>
            <table>
                <tr><th>ID</th><th>Tên</th><th>SĐT</th><th>Zalo</th><th>Ngày ĐK</th><th>Hành động</th></tr>
                {render_customers(customers)}
            </table>
        </div>

        <div id="tab-orders" class="tab-pane">
            <h2 style="margin-top:0;">Danh sách Đơn Hàng</h2>
            <table>
                <tr><th>Khách Hàng</th><th>Sản Phẩm</th><th>Số Tiền</th><th>Ngày</th><th>Trạng Thái</th><th>Hành động</th></tr>
                {render_orders(orders)}
            </table>
        </div>
    </div>

    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.sidebar a').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            document.getElementById('nav-' + tabId).classList.add('active');
        }}
    </script>
</body>
</html>
"""
with open('admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_html_content)

print("Đã tạo xong thanh-toan.html và admin.html bản tĩnh!")
