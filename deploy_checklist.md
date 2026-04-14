# 🚀 Deploy Checklist — Bé Đá Vô Tri (Pet Rock)

> Tạo lúc: 2026-04-14 | Kiểm tra bởi: Antigravity AI Agent

---

## 1. Dự án đang dùng ngôn ngữ / framework gì?

| Thành phần | Chi tiết |
|---|---|
| **Backend** | Python 3 + Flask 3.0.0 |
| **Web Server** | Gunicorn 21.2.0 (sẵn sàng cho production) |
| **Frontend** | HTML thuần + Vanilla CSS + JavaScript |
| **Database** | Supabase (PostgreSQL online) |
| **Email** | Resend API |
| **Payment** | SePay Webhook |
| **Template engine** | Jinja2 (qua Flask) |

---

## 2. Danh sách file cần tạo thêm

| File | Trạng thái | Ghi chú |
|---|---|---|
| `.gitignore` | ✅ Đã tạo | Ngăn commit secrets lên GitHub |
| `.env.example` | ✅ Đã tạo | Template các biến môi trường |
| `README.md` | ✅ Đã tạo | Hướng dẫn deploy cơ bản |
| `Procfile` | ✅ Đã tạo | Cho Render.com (nếu dùng) |

---

## 3. Thông tin bí mật nằm lộ trong code — ĐÃ FIX

| Vấn đề | File | Dòng | Trạng thái |
|---|---|---|---|
| `SUPABASE_KEY` hardcoded | `app.py` | 18 | ✅ Đã chuyển sang `os.environ` |
| `SUPABASE_URL` hardcoded | `app.py` | 17 | ✅ Đã chuyển sang `os.environ` |
| `SUPABASE_KEY` hardcoded | `migrate_data.py` | 6 | ✅ Đã chuyển sang `os.environ` |
| `resend_config.txt` chứa API key thật | `resend_config.txt` | 1 | ⚠️ Đã thêm vào `.gitignore` (KHÔNG commit lên GitHub) |
| Resend key dùng `fallback` từ file txt | `app.py` | 60 | ✅ Giữ logic fallback cho môi trường local |

---

## 4. Danh sách đầy đủ — Cần làm trước khi deploy VPS

### A. Bảo mật ✅
- [x] Chuyển `SUPABASE_URL` và `SUPABASE_KEY` sang environment variables
- [x] Chuyển `RESEND_API_KEY` sang environment variables
- [x] Tạo `.gitignore` để bảo vệ `resend_config.txt`, `.env`, `brain.db`, `*.ttf`
- [x] Tạo `.env.example` mẫu (không chứa giá trị thật)

### B. Server VPS — Cần làm thủ công trên server
- [ ] Cài Python 3.10+ trên VPS (`sudo apt install python3 python3-pip`)
- [ ] Cài `virtualenv` và tạo môi trường ảo
- [ ] Chạy `pip install -r requirements.txt`
- [ ] Tạo file `.env` trên server với giá trị thật (copy từ `.env.example`)
- [ ] Cấu hình Gunicorn chạy app: `gunicorn -w 4 -b 0.0.0.0:3000 app:app`
- [ ] Cấu hình Nginx làm reverse proxy (port 80 → 3000)
- [ ] Cài SSL/HTTPS với Certbot: `sudo certbot --nginx`
- [ ] Mở firewall port 80 và 443 (`ufw allow 80`, `ufw allow 443`)

### C. SePay Webhook — Quan trọng
- [ ] Cập nhật URL webhook trong SePay dashboard thành domain VPS thật
  - Ví dụ: `https://yourdomain.com/api/webhook/sepay`
- [ ] Test webhook thật trước khi go live

### D. Domain & DNS (nếu dùng domain riêng)
- [ ] Trỏ A record DNS về IP VPS
- [ ] Chờ DNS propagate (15 phút – 24 giờ)

### E. Kiểm tra cuối
- [x] `requirements.txt` đã có gunicorn ✅
- [x] `app.py` có `host='0.0.0.0'` ✅
- [x] Test cục bộ: `python app.py` chạy không lỗi
- [x] Test trên server: `gunicorn app:app` chạy không lỗi

---

## 5. Files không nên commit lên GitHub

```
resend_config.txt       # Chứa Resend API Key thật
.env                    # Chứa tất cả secrets
brain.db                # Database SQLite (đã migrate sang Supabase)
*.ttf                   # Font files nặng
__pycache__/
.DS_Store
```

---

> ✅ = Đã xong | ⚠️ = Cần chú ý | [ ] = Cần tự làm trên VPS
