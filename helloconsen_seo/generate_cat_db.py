import json
import os
import time
import re
from qwen_manager import chat_with_qwen

KEYWORDS = [
    {"kw": "Cát mèo", "vol": 60500},
    {"kw": "Cát vệ sinh cho mèo", "vol": 22200},
    {"kw": "Cát đậu nành", "vol": 5400},
    {"kw": "Cát Nhật", "vol": 4400},
    {"kw": "Cát đất sét", "vol": 3600},
    {"kw": "Khử mùi cát mèo", "vol": 2900},
    {"kw": "Cách khử mùi khay vệ sinh cho mèo", "vol": 1300},
    {"kw": "Bột khử mùi cát mèo", "vol": 880},
    {"kw": "Men khử khuẩn cát mèo", "vol": 390},
    {"kw": "Men vi sinh khử mùi cát mèo", "vol": 210}
]

TOTAL_VOL = sum(k['vol'] for k in KEYWORDS)
TARGET_POSTS = 600

db = {
    "pillars": {},
    "clusters": []
}

# Generate super pillars and sub pillars first
print("Generating Pillars...")

for i, kw_info in enumerate(KEYWORDS):
    # Calculate target cluster count
    kw = kw_info['kw']
    count = max(2, int((kw_info['vol'] / TOTAL_VOL) * TARGET_POSTS))
    kw_info['target_count'] = count
    
    # 1. Generate 1 pillar per keyword
    db["pillars"][kw] = {
        "title": f"Toàn tập về {kw} - Giải pháp tối ưu cho người nuôi mèo",
        "url": f"https://helloconsen.com/pillar-{kw.replace(' ', '-')}" # placeholder
    }
    
    print(f"[{kw}] Target articles: {count}")
    
    # Generate titles in batches of 30
    generated_titles = []
    batches = (count // 30) + 1
    
    for b in range(batches):
        needed = min(30, count - len(generated_titles))
        if needed <= 0: break
        
        prompt = f"""
        Bạn là một chuyên gia SEO Copywriter E-commerce.
        Nhiệm vụ của bạn là sáng tạo ra đúng {needed} tiêu đề bài viết (Blog Post) hấp dẫn, kích thích click (Clickbait) và chuẩn SEO chứa từ khóa "{kw}".
        
        YÊU CẦU:
        1. Nhắm vào tệp khách hàng B2C: người nuôi mèo tại chung cư, nhà phố ở Việt Nam.
        2. Các góc tiếp cận đa dạng: Review, Hướng dẫn, Mẹo dân gian, Sai lầm, Cảnh báo bệnh lý, Chia sẻ kinh nghiệm, So sánh.
        3. Tuyệt đối 100% TIẾNG VIỆT, KHÔNG DÙNG TIẾNG ANH.
        4. Trả về đúng danh sách {needed} tiêu đề, mỗi dòng 1 tiêu đề bắt đầu bằng dấu gạch ngang (-). Không viết gì thêm.
        
        VÍ DỤ:
        - 5 Sai lầm khi chọn {kw} khiến cả nhà ngửi mùi khai
        - Review {kw} giá rẻ có thực sự tốt hay rước họa vào thân?
        """
        
        raw = chat_with_qwen(prompt, max_tokens=3000)
        if raw:
            for line in raw.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    title = line[1:].strip()
                    # Clean up bold marks if any
                    title = title.replace('**', '')
                    generated_titles.append(title)
                    db["clusters"].append({
                        "keyword": kw,
                        "title": title,
                        "posted": False
                    })
        time.sleep(2) # rate limit

with open("cat_campaign_db.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=4)

print(f"Total cluster articles generated: {len(db['clusters'])}")
