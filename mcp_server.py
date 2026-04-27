import os
import requests
import uvicorn
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.middleware.trustedhost import TrustedHostMiddleware

load_dotenv(dotenv_path="/opt/my-website/.env")

mcp = FastMCP("Pet Da CRM")

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def supabase_get(table: str, params: str = "") -> list:
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}" if params else f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        return res.json() if res.status_code == 200 else []
    except:
        return []

def supabase_patch(table: str, match: str, data: dict) -> bool:
    url = f"{SUPABASE_URL}/rest/v1/{table}?{match}"
    try:
        res = requests.patch(url, headers=HEADERS, json=data, timeout=10)
        return res.status_code in [200, 204]
    except:
        return False

# ==========================================
# FUNCTIONS CŨ — GIỮ NGUYÊN
# ==========================================

@mcp.tool()
def get_today_orders() -> str:
    """Thống kê số đơn hàng và tổng doanh thu trong ngày hôm nay."""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    orders = supabase_get('orders', f'order_date=gte.{today}T00:00:00Z')
    if not isinstance(orders, list):
        return "Lỗi kết nối Supabase."
    total_revenue = sum(float(o.get('amount', 0)) for o in orders if o.get('status') == 'success')
    return (
        f"📊 Báo cáo ngày {today}:\n"
        f"- Tổng đơn: {len(orders)} đơn\n"
        f"- Doanh thu (đã TT): {'{:,.0f}'.format(total_revenue)} VNĐ"
    )

@mcp.tool()
def check_inventory() -> str:
    """Liệt kê tồn kho các sản phẩm Pet Đá hiện tại."""
    products = supabase_get('products', 'order=id.asc')
    if not products:
        return "Kho trống hoặc lỗi kết nối."
    result = "📦 Tồn kho Pet Đá:\n"
    for p in products:
        result += f"- [ID: {p.get('id')}] {p.get('name')}: {p.get('stock')} bé ({'{:,.0f}'.format(float(p.get('price', 0)))}đ)\n"
    return result

@mcp.tool()
def update_product_price(product_id: int, new_price: float) -> str:
    """Cập nhật giá mới cho một sản phẩm Pet Đá theo ID."""
    products = supabase_get('products', f'id=eq.{product_id}')
    if not products:
        return f"❌ Không tìm thấy sản phẩm ID {product_id}."
    old_price = float(products[0].get('price', 0))
    name = products[0].get('name')
    success = supabase_patch('products', f'id=eq.{product_id}', {"price": new_price})
    if success:
        return f"✅ Đã đổi giá '{name}': {'{:,.0f}'.format(old_price)}đ → {'{:,.0f}'.format(new_price)}đ"
    return "❌ Cập nhật thất bại."

# ==========================================
# FUNCTIONS MỚI — AGENT CHỦ ĐỘNG
# ==========================================

import json

STATE_FILE = "/opt/my-website/state.json"

def get_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"last_order_id": 0, "last_lead_id": 0}

def save_state(state: dict):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except:
        pass

@mcp.tool()
def get_new_orders_since_last_check() -> str:
    """
    Đọc các đơn hàng MỚI chưa được báo cáo dựa trên ID.
    Dùng cho Heartbeat — agent gọi function này mỗi 5 phút.
    Nếu có đơn mới → trả về thông tin chi tiết để agent nhắn Telegram.
    Nếu không có → trả về chuỗi rỗng (agent im lặng, không spam).
    """
    state = get_state()
    last_id = state.get("last_order_id", 0)

    # Lấy đơn mới
    orders = supabase_get(
        'orders',
        f'id=gt.{last_id}&select=*,customers(name,phone_number),products(name)&order=id.asc'
    )
    if not isinstance(orders, list) or len(orders) == 0:
        return ""  # Không có gì mới — agent im lặng

    # Cập nhật ID lớn nhất
    max_id = max([o["id"] for o in orders])
    state["last_order_id"] = max_id
    save_state(state)

    # Tính tổng đơn trong ngày (để context)
    today = datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%d')
    today_orders = supabase_get('orders', f'order_date=gte.{today}T00:00:00&select=id,status')
    today_success = [o for o in today_orders if isinstance(today_orders, list) and o.get('status') == 'success'] if isinstance(today_orders, list) else []

    # Format thông báo
    lines = []
    for o in orders:
        cust = o.get('customers') or {}
        prod = o.get('products') or {}
        cust_name = cust.get('name', 'Khách ẩn danh')
        cust_phone = cust.get('phone_number', 'N/A')
        prod_name = prod.get('name', 'Sản phẩm')
        amount = '{:,.0f}'.format(float(o.get('amount', 0)))
        status = o.get('status', 'pending')
        status_icon = '✅' if status == 'success' else '⏳'
        lines.append(
            f"🛒 Đơn #{o['id']}: {cust_name} ({cust_phone})\n"
            f"   └ {prod_name} · {amount}đ · {status_icon} {status}"
        )

    result = f"🔔 CÓ {len(orders)} ĐƠN MỚI:\n\n" + "\n\n".join(lines)
    result += f"\n\n📊 Hôm nay: {len(today_orders) if isinstance(today_orders, list) else '?'} đơn tổng cộng, {len(today_success)} đã thanh toán."
    return result


@mcp.tool()
def get_new_leads_since_last_check() -> str:
    """
    Đọc các khách hàng/lead MỚI chưa được báo cáo dựa trên ID.
    Dùng cho Heartbeat — agent gọi function này mỗi 5 phút.
    Nếu có lead mới → trả về thông tin để agent nhắn Telegram.
    Nếu không có → trả về chuỗi rỗng (agent im lặng, không spam).
    """
    state = get_state()
    last_id = state.get("last_lead_id", 0)

    leads = supabase_get(
        'customers',
        f'id=gt.{last_id}&select=*&order=id.asc'
    )
    if not isinstance(leads, list) or len(leads) == 0:
        return ""  # Không có lead mới — agent im lặng

    # Cập nhật ID lớn nhất
    max_id = max([lead["id"] for lead in leads])
    state["last_lead_id"] = max_id
    save_state(state)

    # Tổng khách trong ngày
    today = datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%d')
    today_leads = supabase_get('customers', f'registration_date=gte.{today}&select=id')
    today_count = len(today_leads) if isinstance(today_leads, list) else '?'

    lines = []
    for lead in leads:
        name = lead.get('name', 'Khách ẩn danh')
        phone = lead.get('phone_number', 'N/A')
        email = lead.get('email', '')
        email_str = f" · {email}" if email else ""
        lines.append(f"👤 {name} · SĐT: {phone}{email_str}")

    result = f"📬 CÓ {len(leads)} KHÁCH MỚI ĐIỀN FORM:\n\n" + "\n".join(lines)
    result += f"\n\n📊 Hôm nay: {today_count} khách mới tổng cộng."
    return result


@mcp.tool()
def get_daily_summary() -> str:
    """
    Tổng kết 24 giờ qua: đơn hàng, doanh thu, khách mới.
    Dùng cho cron báo sáng 8h mỗi ngày — không cần cờ notified.
    Luôn trả về đầy đủ thông tin dù không có gì mới.
    """
    now_vn = datetime.now(timezone(timedelta(hours=7)))
    yesterday_vn = now_vn - timedelta(hours=24)
    since = yesterday_vn.strftime('%Y-%m-%dT%H:%M:%S')
    today_str = now_vn.strftime('%d/%m/%Y %H:%M')

    # Đơn trong 24h qua
    orders = supabase_get('orders', f'order_date=gte.{since}&select=*,customers(name),products(name)')
    orders = orders if isinstance(orders, list) else []
    success_orders = [o for o in orders if o.get('status') == 'success']
    pending_orders = [o for o in orders if o.get('status') == 'pending']
    total_revenue = sum(float(o.get('amount', 0)) for o in success_orders)

    # Khách mới trong 24h qua
    leads = supabase_get('customers', f'registration_date=gte.{since}&select=name,phone_number')
    leads = leads if isinstance(leads, list) else []

    # Format báo cáo
    result = f"☀️ BÁO SÁNG — {today_str}\n"
    result += f"─────────────────\n"
    result += f"📦 Đơn 24h qua: {len(orders)} đơn\n"
    result += f"   ✅ Thành công: {len(success_orders)} đơn\n"
    result += f"   ⏳ Chờ xử lý: {len(pending_orders)} đơn\n"
    result += f"💰 Doanh thu: {'{:,.0f}'.format(total_revenue)}đ\n"
    result += f"👥 Khách mới: {len(leads)} người\n"

    if len(pending_orders) > 0:
        result += f"\n⚠️ CÒN {len(pending_orders)} ĐƠN CHỜ XỬ LÝ:\n"
        for o in pending_orders[:5]:  # Tối đa 5 đơn để không quá dài
            cust = o.get('customers') or {}
            result += f"   · Đơn #{o['id']}: {cust.get('name', 'Khách')} — {'{:,.0f}'.format(float(o.get('amount', 0)))}đ\n"

    if len(orders) == 0 and len(leads) == 0:
        result += "\n💤 Hôm qua yên tĩnh. Hôm nay bứt phá nhé!"
    else:
        result += "\nChúc bạn một ngày bán hàng ngon lành! 🪨"

    return result


if __name__ == "__main__":
    # Lấy ASGI app từ FastMCP
    app = mcp.streamable_http_app()

    # Thêm TrustedHostMiddleware với allowed_hosts=["*"]
    # để chấp nhận mọi Host header (cần thiết khi đứng sau Nginx proxy)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    # Chạy với uvicorn, bind 127.0.0.1:3002 (Nginx sẽ proxy từ port 3001)
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=3002,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
