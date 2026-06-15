import re
import json

md_file = "từ khóa pain point.md"
db_file = "pain_point_db.json"

def parse_keywords():
    keywords = []
    
    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        # Match markdown table row starting with a number and extracting the keyword column
        # Format: | STT | Từ khóa giải quyết Nỗi Đau (Đã tối ưu GEO) | Lượt tìm kiếm/tháng |
        # Example: | 1 | tại sao mèo ăn nhiều vẫn gầy [Địa phương] | 2,900 |
        
        match = re.match(r'^\|\s*\d+\s*\|\s*(.*?)\s*\|.*\|', line.strip())
        if match:
            kw = match.group(1).strip()
            # Replace placeholder if they left it literal
            if "[Địa phương]" in kw:
                kw = kw.replace("[Địa phương]", "TPHCM") # Defaulting to TPHCM or let AI handle it? Let's fix it to TPHCM for local SEO
                
            keywords.append({
                "keyword": kw,
                "articles_written": 0,
                "history": []
            })
            
    print(f"[*] Đã trích xuất {len(keywords)} từ khóa từ file Markdown.")
    
    # Save to JSON
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump({"keywords": keywords}, f, ensure_ascii=False, indent=4)
        
    print(f"[*] Đã lưu vào {db_file}")

if __name__ == "__main__":
    parse_keywords()
