# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, requests
from dotenv import load_dotenv
load_dotenv()

WP_URL = "https://giaiphapqrcode.com"
WP_USERNAME = os.getenv("WP_USERNAME", "bluedata")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

print("=== KIEM TRA HE THONG GIAIPHAPQRCODE ===\n")
print(f"WP_USERNAME: {WP_USERNAME}")
print(f"WP_APP_PASSWORD: {'OK (' + WP_APP_PASSWORD[:8] + '...)' if WP_APP_PASSWORD else 'KHONG CO!'}")
print(f"QWEN_API_KEY: {'OK (' + QWEN_API_KEY[:15] + '...)' if QWEN_API_KEY else 'KHONG CO!'}")
print()

# Test WordPress API
print("--- WordPress API ---")
try:
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts",
                     auth=(WP_USERNAME, WP_APP_PASSWORD),
                     params={"per_page": 3, "orderby": "date", "order": "desc"},
                     timeout=20)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        posts = r.json()
        for p in posts:
            print(f"  - [{p['date']}] {p['title']['rendered'][:60]}")
    else:
        print(f"Loi: {r.text[:200]}")
except Exception as e:
    print(f"FAILED: {e}")

print()
print("--- Qwen API ---")
try:
    from openai import OpenAI
    client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )
    resp = client.chat.completions.create(
        model="qwen-max",
        messages=[{"role": "user", "content": "Say OK only."}]
    )
    print(f"Status: OK - {resp.choices[0].message.content}")
except Exception as e:
    print(f"FAILED: {e}")

print()
print("--- Files he thong ---")
files_check = [
    "keyword_clusters.json",
    "danh_sach_tu_khoa.txt",
    "fully_auto_giaiphapqrcode.py",
    "chay_he_thong_giaiphapqrcode.bat",
    ".env"
]
for f in files_check:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    print(f"  {'[OK]' if exists else '[MISSING]'} {f} ({size} bytes)")
