import csv

input_file = r"D:\Antigravity\giaiphapqrcode_seo\gemini-code-1777629293599.txt"
output_file = r"D:\Antigravity\giaiphapqrcode_seo\danh_sach_tu_khoa.txt"

keywords = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader) # Skip header
    for row in reader:
        if len(row) >= 3:
            keywords.append(row[2].strip())

with open(output_file, 'w', encoding='utf-8') as f:
    for kw in keywords:
        f.write(kw + '\n')

print(f"Extracted {len(keywords)} keywords to {output_file}")
