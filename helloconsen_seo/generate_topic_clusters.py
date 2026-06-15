import os
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
    print(f"[*] Đang yêu cầu AI vắt não nghĩ 100 Insights cho từ khóa: '{keyword}'...")
    prompt = f"""
Nhiệm vụ: Bạn là một chuyên gia Content SEO Marketing đẳng cấp quốc tế.
Bạn cần xây dựng một ma trận Content (Topical Authority) cho từ khóa: "{keyword}".

YÊU CẦU:
Hãy nghĩ ra đúng 100 Content Directions (Góc nhìn / Quan điểm / Đối tượng / Tình huống / Insight) hoàn toàn khác biệt nhau để viết 100 bài báo khác nhau xoay quanh từ khóa này mà không bị trùng lặp nội dung.
Mỗi Insight chỉ dài 1 câu ngắn gọn.
Ví dụ:
- Dành cho đối tượng sinh viên ít tiền.
- Góc nhìn từ sai lầm dân gian truyền miệng.
- Cách chữa cho mèo đang mang thai.
- So sánh các phương pháp trên thị trường.

ĐẦU RA BẮT BUỘC: 
Chỉ trả về 1 mảng JSON (JSON Array Code) bao gồm 100 chuỗi string. Tuyệt đối không có text nào khác ngoài Array này.
[
    "Góc nhìn 1...",
    "Góc nhìn 2...",
    ...
]
    """
    for attempt in range(3):
        try:
            raw = chat_with_qwen(prompt, max_tokens=2000, temperature=0.8)
            if not raw:
                continue
            arr = extract_json_array(raw)
            if arr and isinstance(arr, list) and len(arr) > 50:
                print(f"  [+] Thành công! Qwen đã sinh ra {len(arr)} insights.")
                return arr
            else:
                print(f"  [-] Lỗi: AI không trả về đúng mảng JSON hoặc quá ít ({len(arr) if arr else 0}). Thử lại...")
        except Exception as e:
            print(f"  [-] Lỗi kết nối: {e}")
        time.sleep(3)
    
    return [f"Insight cơ bản gốc cho {keyword}"] * 100

def main():
    if not os.path.exists(KEYWORD_FILE):
        print(f"[-] Không tìm thấy {KEYWORD_FILE}")
        return
        
    with open(KEYWORD_FILE, "r", encoding="utf-8") as f:
        keywords = [k.strip() for k in f.readlines() if k.strip()]
        
    clusters = load_clusters()
    
    for kw in keywords:
        if kw in clusters and len(clusters[kw]) > 10:
            print(f"[*] Bỏ qua: '{kw}' đã có sẵn {len(clusters[kw])} insights.")
            continue
            
        insights = generate_insights(kw)
        clusters[kw] = insights
        save_clusters(clusters)
        
    print("\n✅ HOÀN TẤT! Đã sinh xong bộ từ khóa ma trận.")
    print("Bạn có thể mở file 'keyword_clusters.json' để xem các góc nhìn.")

if __name__ == "__main__":
    main()
