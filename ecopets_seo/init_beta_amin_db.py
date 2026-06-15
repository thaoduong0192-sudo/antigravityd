import os
import json
import re
import math

input_file = "Đánh sản phẩm Sốt đạm thủy phân sấy.md"
output_file = "beta_amin_db.json"

TOTAL_ARTICLES = 596

def init_db():
    keywords = []
    
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Find all table rows with 4 columns starting with a number
    # Format: | 1 | chó kén ăn | 12.500 | Giải thích... |
    pattern = r"\|\s*\d+\s*\|\s*([^\|]+?)\s*\|\s*([0-9\.]+)\s*\|\s*([^\|]+?)\s*\|"
    matches = re.findall(pattern, content)
    
    total_sv = 0
    parsed_kws = []
    
    for kw, sv_str, insight in matches:
        # Clean sv_str (remove dots)
        sv = int(sv_str.replace(".", ""))
        total_sv += sv
        parsed_kws.append({
            "keyword": kw.strip(),
            "sv": sv,
            "insight": insight.strip()
        })
        
    print(f"Total SV: {total_sv}, Total Keywords: {len(parsed_kws)}")
    
    # Calculate target_articles based on proportion of SV
    # To handle rounding issues, we'll assign the integer part first, then distribute the remainder
    db_keywords = []
    total_assigned = 0
    
    for item in parsed_kws:
        exact_share = (item["sv"] / total_sv) * TOTAL_ARTICLES
        assigned = math.floor(exact_share)
        total_assigned += assigned
        
        db_keywords.append({
            "keyword": item["keyword"],
            "search_volume": item["sv"],
            "target_articles": assigned,
            "articles_written": 0,
            "core_insight": item["insight"]
        })
        
    # Distribute remaining articles to top SV keywords
    remainder = TOTAL_ARTICLES - total_assigned
    db_keywords.sort(key=lambda x: x["search_volume"], reverse=True)
    
    for i in range(remainder):
        db_keywords[i]["target_articles"] += 1
        
    # Sort back by original logic (we can just leave it sorted by SV, it's fine)
    
    db = {
        "campaign_name": "Beta Amin Content Campaign",
        "total_target": TOTAL_ARTICLES,
        "keywords": db_keywords
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
        
    print(f"Created {output_file} with {len(db_keywords)} keywords. Total target: {sum(k['target_articles'] for k in db_keywords)}")

if __name__ == "__main__":
    init_db()
