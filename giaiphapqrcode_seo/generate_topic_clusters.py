import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import time
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
KEYWORD_FILE = "danh_sach_tu_khoa.txt"
CLUSTER_FILE = "keyword_clusters.json"

if not QWEN_API_KEY:
    print("[-] LỖI: Chưa có QWEN_API_KEY trong .env")
    exit()

from qwen_manager import chat_with_qwen

def load_clusters():
    if os.path.exists(CLUSTER_FILE):
        try:
            with open(CLUSTER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_clusters(data):
    with open(CLUSTER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def extract_json_array(text):
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None
    return None

def generate_insights(keyword):
    print(f"[*] Sinh 20 insights cho: '{keyword}'...")
    prompt = (
        f'Ban la chuyen gia SEO Marketing. Hay tao DUNG 20 goc nhin (insight) '
        f'khac nhau de viet 20 bai blog ve chu de: "{keyword}".\n'
        'Moi insight la 1 cau ngan gon bang tieng Viet.\n'
        'Chi tra ve JSON array, KHONG co text nao khac:\n'
        '["insight 1", "insight 2", ..., "insight 20"]'
    )
    for attempt in range(4):
        try:
            raw = chat_with_qwen(prompt, max_tokens=3000, temperature=0.8)
            if not raw:
                print(f"  [-] Qwen tra None lan {attempt+1}, thu lai...")
                time.sleep(5)
                continue
            arr = extract_json_array(raw)
            if arr and isinstance(arr, list) and len(arr) > 5:
                print(f"  [+] Thanh cong! {len(arr)} insights.")
                return arr
            else:
                count = len(arr) if arr else 0
                print(f"  [-] JSON khong du ({count} items). Raw: {raw[:150]}")
        except Exception as e:
            print(f"  [-] Loi: {e}")
        time.sleep(3)

    # Fallback: tao insights thu cong tu tu khoa
    print(f"  [!] Dung fallback thu cong cho: {keyword}")
    return [
        f"Huong dan trien khai {keyword} cho doanh nghiep vua va nho",
        f"So sanh {keyword} voi phuong phap truyen thong",
        f"Loi ich cua {keyword} doi voi nganh ban le",
        f"Chi phi trien khai {keyword} va ROI thuc te",
        f"Cach chon nha cung cap {keyword} uy tin tai Viet Nam",
        f"Nhung loi thuong gap khi trien khai {keyword}",
        f"{keyword} giup doanh nghiep tang trai nghiem khach hang",
        f"Quy trinh trien khai {keyword} tu A den Z",
        f"Case study: Doanh nghiep thanh cong nho {keyword}",
        f"{keyword} va xu huong so hoa doanh nghiep 2025",
        f"Tich hop {keyword} voi he thong ERP/CRM hien co",
        f"Bao mat du lieu khi su dung {keyword}",
        f"{keyword} phu hop voi quy mo doanh nghiep nao",
        f"Diem manh va han che cua {keyword}",
        f"Cach do luong hieu qua sau khi trien khai {keyword}",
        f"{keyword} trong boi canh chuyen doi so tai Viet Nam",
        f"Huong dan khach hang su dung {keyword} de dang",
        f"Phap ly va tuan thu quy dinh khi dung {keyword}",
        f"Tuong lai cua {keyword} trong 5 nam toi",
        f"FAQ: Nhung cau hoi thuong gap ve {keyword}",
    ]

def main():
    if not os.path.exists(KEYWORD_FILE):
        print(f"[-] Không tìm thấy {KEYWORD_FILE}")
        return
        
    with open(KEYWORD_FILE, "r", encoding="utf-8") as f:
        keywords = [k.strip() for k in f.readlines() if k.strip()]
        
    clusters = load_clusters()
    
    for kw in keywords:
        if kw in clusters and isinstance(clusters[kw], list) and len(clusters[kw]) > 5:
            sample = clusters[kw][0] if clusters[kw] else ''
            if 'Insight c' not in sample and 'co ban goc' not in sample:
                print(f"[=] Bo qua: '{kw[:50]}' da co {len(clusters[kw])} insights that.")
                continue
            else:
                print(f"[!] '{kw[:50]}' co fallback, sinh lai...")
            
        insights = generate_insights(kw)
        clusters[kw] = insights
        save_clusters(clusters)
        
    print("\n✅ HOÀN TẤT! Đã sinh xong bộ từ khóa ma trận.")
    print("Bạn có thể mở file 'keyword_clusters.json' để xem các góc nhìn.")

if __name__ == "__main__":
    main()
