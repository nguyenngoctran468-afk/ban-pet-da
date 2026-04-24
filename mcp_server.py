import os
import requests
import uvicorn
from datetime import datetime, timezone
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
        result += f"- {p.get('name')}: {p.get('stock')} bé ({'{:,.0f}'.format(float(p.get('price', 0)))}đ)\n"
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
