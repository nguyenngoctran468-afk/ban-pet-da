import time
from pyngrok import ngrok
import sys

def main():
    token = sys.argv[1]
    ngrok.set_auth_token(token)
    
    # Mở tunnel ở cổng 3000
    try:
        http_tunnel = ngrok.connect(3000)
        print(f"NGROK_URL: {http_tunnel.public_url}", flush=True)
        print("Đường hầm Ngrok đã mở thành công và đang giữ kết nối...", flush=True)
        # Keep process alive
        while True:
            time.sleep(10)
    except Exception as e:
        print(f"Lỗi khi mở Ngrok: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main()
    else:
        print("Thiếu token!")
