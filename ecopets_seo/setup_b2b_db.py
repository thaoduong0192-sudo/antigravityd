import os
import json
import re

def parse_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    keywords = []
    current_group = ""
    current_insight = ""

    for i in range(len(lines)):
        line = lines[i].strip()
        if not line:
            continue

        if line.startswith("Nhóm"):
            current_group = line
            # The next line is the insight description
            if i + 1 < len(lines):
                current_insight = lines[i+1].strip()
            continue

        # Check if line is a number (STT)
        if line.isdigit():
            # The next line should be the keyword
            if i + 1 < len(lines):
                kw = lines[i+1].strip()
                if kw and not kw.isdigit() and kw != "Cụm từ khóa (Keywords)" and kw != "STT":
                    keywords.append({
                        "id": int(line),
                        "keyword": kw,
                        "group": current_group,
                        "insight": current_insight,
                        "published_count": 0
                    })
                
    # Sort by ID just in case
    keywords.sort(key=lambda x: x["id"])
    return keywords

def main():
    file_path = "D:\\Antigravity\\ecopets_seo\\Tìm Từ Khóa B2B Ngành Thú Cưng.txt"
    db_path = "D:\\Antigravity\\ecopets_seo\\b2b_campaign_db.json"
    
    # If the file already exists, don't overwrite the entire thing directly, just update missing ones.
    # But since this is a new feature, we can just create it if it doesn't exist.
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            existing_db = json.load(f)
        print(f"Database đã tồn tại với {len(existing_db['keywords'])} từ khóa.")
    else:
        kws = parse_keywords(file_path)
        # Verify 100
        print(f"Đã bóc tách được {len(kws)} từ khóa.")
        
        # Save
        db = {"keywords": kws, "published_articles": []}
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
        print("Đã tạo b2b_campaign_db.json thành công!")

if __name__ == "__main__":
    main()
