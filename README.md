# 🪨 Bé Đá Vô Tri — Pet Rock Landing Page

Website bán Pet Rock (Đá Cưng) dành cho dân văn phòng Gen Z. Stack: Python Flask + Supabase + Resend Email + SePay Payment.

---

## 🏗️ Cấu trúc dự án

```
├── app.py              # Backend chính (Flask)
├── templates/          # HTML templates (admin, checkout)
│   ├── admin.html
│   └── checkout.html
├── index.html          # Landing page chính
├── style.css           # CSS
├── requirements.txt    # Python dependencies
├── .env.example        # Template biến môi trường (copy thành .env)
├── Procfile            # Cho Render.com
└── deploy_checklist.md # Checklist deploy đầy đủ
```

---

## ⚡ Deploy lên VPS Linux (Ubuntu)

### Bước 1 — Chuẩn bị VPS

```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài Python 3 + pip + virtualenv
sudo apt install python3 python3-pip python3-venv nginx -y
```

### Bước 2 — Upload code lên VPS

```bash
# Cách 1: Dùng Git (khuyên dùng)
git clone https://github.com/your-username/ban-pet-da.git
cd ban-pet-da

# Cách 2: Dùng SCP (copy thẳng từ máy)
scp -r ./ user@your-vps-ip:/home/user/ban-pet-da/
```

### Bước 3 — Tạo môi trường ảo và cài thư viện

```bash
cd /home/user/ban-pet-da

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

### Bước 4 — Cấu hình Environment Variables

```bash
# Copy file mẫu
cp .env.example .env

# Mở file và điền giá trị thật
nano .env
```

Nội dung file `.env` cần điền:
```
SUPABASE_URL=https://aahbbepwytfpuzjuxocv.supabase.co
SUPABASE_KEY=your_actual_supabase_key
RESEND_API_KEY=your_actual_resend_key
```

### Bước 5 — Test chạy thử

```bash
# Load env vars và chạy thử
export $(cat .env | xargs)
python app.py
# → Truy cập http://your-vps-ip:3000 để kiểm tra
```

### Bước 6 — Chạy với Gunicorn (Production)

```bash
# Chạy thử Gunicorn
gunicorn -w 2 -b 0.0.0.0:3000 app:app

# Cài systemd service để tự khởi động lại khi reboot
sudo nano /etc/systemd/system/petda.service
```

Nội dung file `petda.service`:
```ini
[Unit]
Description=Pet Da Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ban-pet-da
EnvironmentFile=/home/ubuntu/ban-pet-da/.env
ExecStart=/home/ubuntu/ban-pet-da/venv/bin/gunicorn -w 2 -b 0.0.0.0:3000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable petda
sudo systemctl start petda
sudo systemctl status petda  # Kiểm tra đang chạy
```

### Bước 7 — Cấu hình Nginx (Reverse Proxy)

```bash
sudo nano /etc/nginx/sites-available/petda
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/petda /etc/nginx/sites-enabled/
sudo nginx -t         # Kiểm tra config hợp lệ
sudo systemctl restart nginx
```

### Bước 8 — Cài SSL miễn phí với Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
# Làm theo hướng dẫn → HTTPS tự động hoạt động
```

### Bước 9 — Cập nhật SePay Webhook URL

Vào dashboard SePay → Cập nhật URL webhook:
```
https://yourdomain.com/api/webhook/sepay
```

---

## 🔄 Deploy lên Render.com (Cách nhanh hơn VPS)

1. Push code lên GitHub (đảm bảo `.gitignore` đã có)
2. Vào [render.com](https://render.com) → New Web Service
3. Connect GitHub repo
4. Cấu hình:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
5. Thêm Environment Variables trong dashboard Render
6. Deploy!

---

## 🔧 Lệnh hữu ích

```bash
# Xem logs app đang chạy
sudo journalctl -u petda -f

# Restart app sau khi sửa code
sudo systemctl restart petda

# Cập nhật code mới
git pull origin main
sudo systemctl restart petda

# Kiểm tra Nginx logs
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 Liên hệ

Team Pet Đá — nguyenngoctran468@gmail.com
