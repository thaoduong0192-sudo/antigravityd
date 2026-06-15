# -*- coding: utf-8 -*-
"""
test_run_one.py - Chạy thử đăng 1 bài để xem lỗi gì
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, json, random, requests, time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

WP_URL          = "https://giaiphapqrcode.com"
WP_USERNAME     = os.getenv("WP_USERNAME", "bluedata")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
QWEN_API_KEY    = os.getenv("QWEN_API_KEY")

client = OpenAI(
    api_key=QWEN_API_KEY,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

# Load keyword_clusters
with open("keyword_clusters.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loai du lieu: {type(data).__name__}, so phan tu: {len(data)}")

# Xem cau truc
if isinstance(data, list):
    print("Cau truc LIST - phan tu dau:")
    print(json.dumps(data[0], ensure_ascii=False, indent=2)[:500])
    keyword = data[0] if isinstance(data[0], str) else str(data[0])
    insight = "Cach trien khai QR code cho doanh nghiep vua va nho"
elif isinstance(data, dict):
    print("Cau truc DICT - key dau:")
    first_key = list(data.keys())[0]
    print(f"Key: {first_key}")
    print(json.dumps(data[first_key], ensure_ascii=False, indent=2)[:500])
    keyword = first_key
    val = data[first_key]
    if isinstance(val, list):
        insight = val[0] if val else keyword
    elif isinstance(val, dict):
        insights = val.get("insights", [])
        insight = insights[0] if insights else keyword
    else:
        insight = str(val)

print(f"\nThu viet bai:")
print(f"  Tu khoa: {keyword[:60]}")
print(f"  Insight: {insight[:80]}")

# Thu goi Qwen
print("\nGoi Qwen API...")
try:
    resp = client.chat.completions.create(
        model="qwen-max",
        messages=[{"role": "user", "content": f"Viet 1 doan 50 chu ve: {keyword} - {insight}"}],
        timeout=30
    )
    print(f"Qwen OK: {resp.choices[0].message.content[:100]}")
except Exception as e:
    print(f"Qwen LOI: {e}")

# Thu dang len WordPress
print("\nThu dang bai len WordPress...")
try:
    payload = {
        "title": f"Test - {keyword[:50]}",
        "content": f"<p>Day la bai test tu dong. Insight: {insight}</p>",
        "status": "draft"  # draft de khong hien thi that
    }
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        json=payload, timeout=20
    )
    print(f"WordPress dang bai: {r.status_code}")
    if r.status_code == 201:
        post_id = r.json()["id"]
        print(f"  Bai draft ID: {post_id} - OK!")
        # Xoa bai draft ngay
        r2 = requests.delete(
            f"{WP_URL}/wp-json/wp/v2/posts/{post_id}?force=true",
            auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10
        )
        print(f"  Xoa bai draft: {r2.status_code}")
    else:
        print(f"  LOI: {r.text[:300]}")
except Exception as e:
    print(f"WordPress LOI: {e}")

print("\n=== XONG KIEM TRA ===")
