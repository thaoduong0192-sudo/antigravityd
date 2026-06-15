import os
import re
import json

def parse_database(file_path):
    keywords = []
    petshops = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract keywords
    # Matches lines like: 1. # Pet shop Quận \[X\] / Pet shop tại
    keyword_pattern = re.compile(r'^\d+\.\s*#\s*(.+)$', re.MULTILINE)
    for match in keyword_pattern.finditer(content):
        kw = match.group(1).strip()
        kw = kw.replace('\\[', '[').replace('\\]', ']')
        # Remove any literal backslashes if present
        kw = kw.replace('\\', '')
        keywords.append(kw)
        
    # Extract petshops from tables
    lines = content.split('\n')
    in_table = False
    for line in lines:
        if line.startswith('| Tên Cơ Sở / Cửa Hàng |'):
            in_table = True
            continue
        if in_table and line.startswith('| :----'):
            continue
        if in_table and line.startswith('|'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                name = parts[1].strip()
                address = parts[2].strip()
                phone = parts[3].strip()
                if name and name != 'Tên Cơ Sở / Cửa Hàng':
                    # clean up phone numbers like "Đang cập nhật 5" or "077 224 4474 15"
                    phone = re.sub(r'\s*\d+$', '', phone).strip() # Removes trailing space and numbers
                    if "Đang cập nhật" in phone or not phone:
                        phone = "Đang cập nhật"
                    petshops.append({
                        "name": name,
                        "address": address,
                        "phone": phone
                    })
        else:
            in_table = False

    return keywords, petshops

if __name__ == '__main__':
    md_file = r"c:\Users\US\Downloads\Xây dựng Database Petshop Toàn Quốc (2).md"
    keywords, petshops = parse_database(md_file)
    
    # Save parsed database
    db_path = r"d:\Antigravity\helloconsen_seo\b2b_database.json"
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump({
            "keywords": keywords,
            "petshops": petshops
        }, f, ensure_ascii=False, indent=4)
        
    print(f"Extracted {len(keywords)} keywords and {len(petshops)} petshops.")
    
    # Initialize campaign state
    state_path = r"d:\Antigravity\helloconsen_seo\b2b_campaign_state.json"
    if not os.path.exists(state_path):
        state = {
            "keywords_status": {kw: {"articles_posted": 0} for kw in keywords},
            "current_shop_index": 0,
            "total_articles_posted": 0
        }
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=4)
        print("Initialized new campaign state.")
    else:
        print("Campaign state already exists. Skipping initialization.")
