# Gợi ý MCP Functions cho Pet Đá CRM

Dựa trên cấu trúc dự án (bán hàng Pet Đá, có CRM đơn giản, form waitlist, luồng gửi email tự động), dưới đây là 4 function hữu ích nhất để bạn có thể thao tác qua Telegram mà không cần mở máy tính:

### 1. `get_today_orders`
- **Input params:** Không cần (tự động lấy ngày hôm nay)
- **Output dự kiến:** Chuỗi text báo cáo tổng số đơn hàng, tổng doanh thu và danh sách các món đồ bán được trong ngày.
- **Tình huống dùng hàng ngày:** Đang đi nhậu với bạn bè, mở Telegram hỏi "Hôm nay bán được mấy cục đá rồi?" để xem thành quả kinh doanh.
- **Độ ưu tiên:** 5/5

### 2. `check_inventory`
- **Input params:** Không cần (hoặc `product_id` - optional)
- **Output dự kiến:** Danh sách các sản phẩm và số lượng tồn kho (stock) hiện tại.
- **Tình huống dùng hàng ngày:** Nhắn "Kho còn bao nhiêu bé đá?" để biết chừng lôi kéo khách hàng báo hết hàng tạo FOMO.
- **Độ ưu tiên:** 4/5

### 3. `send_custom_email`
- **Input params:** 
  - `customer_id` (int): ID khách hàng
  - `subject` (string): Tiêu đề email
  - `content` (string): Nội dung email
- **Output dự kiến:** Thông báo gửi email thành công/thất bại.
- **Tình huống dùng hàng ngày:** Thấy một khách hàng quen lâu không tương tác, nhắn AI "Gửi email chúc mừng sinh nhật cho khách ID 12 nhé, viết giọng vô tri vào".
- **Độ ưu tiên:** 4/5

### 4. `update_order_status`
- **Input params:** 
  - `order_id` (int): Mã đơn hàng
  - `status` (string): 'success', 'pending', hoặc 'cancelled'
- **Output dự kiến:** Thông báo cập nhật thành công và số lượng tồn kho thay đổi tương ứng.
- **Tình huống dùng hàng ngày:** Khách chuyển khoản ngoài SePay (ví dụ đưa tiền mặt), bạn nhắn "Chuyển đơn số 15 sang thành công nhé".
- **Độ ưu tiên:** 3/5
