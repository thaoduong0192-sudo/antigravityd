import json
import time
import os
import re
from qwen_manager import chat_with_qwen

def extract_json_array(text):
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None
    return None

def main():
    print("🚀 Bắt đầu sinh 1000 từ khóa ngách (Long-tail) từ 100 từ khóa gốc...")
    
    # Load 100 base keywords
    db_path = 'D:\\Antigravity\\ecopets_seo\\b2b_campaign_db.json'
    if not os.path.exists(db_path):
        print("Lỗi: Không tìm thấy database cũ.")
        return
        
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
        
    base_keywords = [k['keyword'] for k in db.get('keywords', [])]
    
    # Output file
    out_path = 'D:\\Antigravity\\ecopets_seo\\b2b_cluster_db.json'
    out_data = {"clusters": []}
    
    if os.path.exists(out_path):
        with open(out_path, 'r', encoding='utf-8') as f:
            out_data = json.load(f)
            
    existing_pillars = [c['pillar_keyword'] for c in out_data['clusters']]
    
    for kw in base_keywords:
        if kw in existing_pillars:
            print(f"Bỏ qua '{kw}', đã có dữ liệu.")
            continue
            
        print(f"\n[*] Đang chẻ từ khóa: {kw}")
        prompt = f"""
Bạn là chuyên gia SEO Research ngành kinh doanh thú cưng (Petshop, Phòng khám thú y) tại Việt Nam.
Từ khóa gốc (Pillar): "{kw}"

Nhiệm vụ: Hãy sinh ra ĐÚNG 9 TỪ KHÓA NGÁCH (Long-tail keywords) xoay quanh từ khóa gốc này.
Yêu cầu:
- Các từ khóa phải CÓ LƯỢNG TÌM KIẾM THỰC TẾ (chứa các cụm từ như: tại tphcm, giá rẻ, uy tín, kinh nghiệm, mua ở đâu, lấy sỉ, cách...).
- Dài từ 5-9 chữ. Tự nhiên như cách người dùng gõ Google.
- CHỈ TRẢ VỀ DUY NHẤT 1 MẢNG JSON. Không giải thích.

Đầu ra mẫu:
[
    "từ khóa ngách 1",
    "từ khóa ngách 2",
    ...
]
"""
        longtails = []
        for _ in range(3):
            raw = chat_with_qwen(prompt, max_tokens=2000, temperature=0.7)
            if not raw:
                time.sleep(2)
                continue
            arr = extract_json_array(raw)
            if arr and isinstance(arr, list) and len(arr) >= 5:
                longtails = arr[:9]
                break
            time.sleep(2)
            
        if not longtails:
            print(f"  [-] Lỗi sinh từ khóa cho {kw}")
            # Fallback
            longtails = [f"{kw} uy tín", f"{kw} tại tphcm", f"kinh nghiệm {kw}", f"bảng giá {kw}", f"hướng dẫn {kw}"]
            
        print(f"  [+] Đã sinh {len(longtails)} ngách: {longtails[:2]}...")
        
        # Prepare objects
        cluster_obj = {
            "pillar_keyword": kw,
            "pillar_published": False,
            "clusters": [{"keyword": lt, "published": False} for lt in longtails]
        }
        out_data["clusters"].append(cluster_obj)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(out_data, f, ensure_ascii=False, indent=4)
            
        time.sleep(1)
        
    print("✅ Hoàn tất sinh dữ liệu Cluster.")

if __name__ == "__main__":
    main()
