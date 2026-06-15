import csv
import json

csv_file = "100 tu khoa.csv"
json_file = "keyword_clusters.json"

all_keywords = {}

try:
    with open(csv_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i == 0: continue # skip header
            line = line.strip()
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            parts = line.split(',')
            if len(parts) >= 2:
                keyword = parts[1].strip()
                if keyword:
                    insights = [
                        f"Góc nhìn phân tích chuyên sâu về lý do tại sao người nuôi cần biết về {keyword}",
                        f"Hướng dẫn thực tế từng bước để giải quyết {keyword} hiệu quả",
                        f"Sai lầm phổ biến thường gặp liên quan đến {keyword} và cách phòng tránh",
                        f"Kinh nghiệm thực chiến từ chuyên gia để xử lý {keyword} tối ưu nhất",
                        f"So sánh ưu và nhược điểm của các phương pháp hiện tại xoay quanh {keyword}",
                        f"Những hiểu lầm tai hại về {keyword} mà nhiều người chưa biết",
                        f"Cập nhật những xu hướng và công nghệ mới nhất áp dụng cho {keyword} năm 2026",
                        f"Câu chuyện thực tế từ góc nhìn của chủ thú cưng đã thành công xử lý {keyword}",
                        f"Góc độ kinh tế tài chính: Làm sao để tối ưu chi phí khi giải quyết {keyword}",
                        f"Tác động dài hạn của {keyword} đối với sức khỏe và trải nghiệm sống của thú cưng"
                    ]
                    all_keywords[keyword] = insights

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_keywords, f, ensure_ascii=False, indent=4)
    print(f"Thành công: Đã tạo keyword_clusters.json với {len(all_keywords)} từ khóa từ CSV!")
except Exception as e:
    print(f"Lỗi: {e}")
