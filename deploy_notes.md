# Ghi chú Triển khai (Deploy Notes) - ban-pet-da

File này liệt kê thông tin cần thiết để khởi chạy app trên VPS Ubuntu.

## 1. Môi trường (.env) cần thiết
Cần tạo một file `.env` tại thư mục `/opt/ban-pet-da` trên VPS với các giá trị như sau:
```env
SUPABASE_URL=https://aahbbepwytfpuzjuxocv.supabase.co
SUPABASE_KEY=[điền giá trị thật nếu có]
RESEND_API_KEY=re_BddmycKv_84x9NT3Dh1ZFeT8C7Tixu8Jc
PORT=3000
```

## 2. Thông tin Server
- **Ngôn ngữ/Framework**: Python 3 (Flask)
- **Cổng lắng nghe**: `3000`

## 3. Các lệnh để chạy (Systemd Service)
- Cài đặt thư viện: `pip3 install -r requirements.txt` (khuyến nghị dùng môi trường ảo `virtualenv`)
- Chạy bằng Gunicorn: `gunicorn -w 4 -b 0.0.0.0:3000 app:app`

## 4. Chú ý Data
File database gốc là `brain.db`. GitHub KHÔNG lưu file này. Phải upload `brain.db` từ máy cá nhân lên VPS (bằng `scp`).
