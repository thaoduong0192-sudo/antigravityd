import json
import os

topics = [
    "viêm tai chó", "viêm tai mèo", "nấm tai chó mèo", "cách vệ sinh tai cho chó", "bọt vệ sinh tai thuần chay",
    "chó bị thiếu canxi", "chó con còi xương", "bổ sung canxi cho chó bầu", "canxi hữu cơ ngừa sỏi thận", "chó bị hạ canxi máu",
    "phục hồi sức khỏe chó ốm", "mèo lười ăn", "beta amin chó mèo", "tăng đề kháng cho mèo", "chó bị sút cân",
    "chó bị nấm da", "mèo bị rụng lông", "xịt khử khuẩn da chó mèo", "viêm da cơ địa ở chó", "trị ghẻ chó tại nhà",
    "chó bị tiêu chảy", "mèo bị đi ngoài", "men vi sinh cho mèo", "chữa viêm ruột chó", "chó bị nôn mửa bọt trắng",
    "sữa tắm khô chó mèo", "khử mùi hôi lông chó", "mèo sợ tắm", "làm sạch chân chó sau khi đi dạo", "tắm cho chó con an toàn",
    "chó bị ho khạc", "mèo thở khò khè", "chó bị sốt", "dấu hiệu mèo bị ốm", "cách hạ sốt cho chó",
    "mèo bị sỏi thận", "chó bị bí tiểu", "thức ăn cho chó suy thận", "ngừa sỏi bàng quang mèo", "chăm sóc chó già",
    "thức ăn hạt cho chó", "pate cho mèo", "chế độ ăn raw cho chó", "mèo bị dị ứng thức ăn", "chó béo phì giảm cân",
    "huấn luyện chó đi vệ sinh", "mèo cắn phá đồ đạc", "chó sủa nhiều", "mèo bị stress", "dạy chó lệnh cơ bản",
    "chăm sóc mèo đẻ", "chó mang thai nên ăn gì", "mèo con bú bình", "chó mẹ ít sữa", "dấu hiệu chó sắp sinh",
    "tẩy giun cho chó", "lịch tiêm phòng mèo", "nhỏ gáy trị rận mèo", "chó bị ve rận", "phòng bệnh dại chó mèo",
    "chó cắn nhau chảy máu", "mèo bị gãy xương", "sơ cứu chó bị hóc xương", "chó bị ong đốt", "mèo nuốt phải dị vật",
    "tuổi thọ của chó", "mèo già bị lẫn", "chó bị đục thủy tinh thể", "viêm khớp ở chó già", "thức ăn cho mèo lớn tuổi",
    "chó poodle bị bạc lông", "chó pug hay rụng lông", "mèo anh lông ngắn bị nấm", "chăm sóc lông chó phốc sóc", "mèo ba tư bị chảy nước mắt",
    "chó husky lười ăn", "chó golden rụng lông", "mèo sphynx chăm sóc da", "chó corgi bị béo phì", "mèo scottish bị thoái hóa khớp",
    "đồ chơi cho chó nhai", "bàn cào móng cho mèo", "chuồng chó inox", "cát vệ sinh cho mèo khử mùi", "balo vận chuyển chó mèo",
    "máy lọc nước cho mèo", "bát ăn chậm cho chó", "nệm ngủ cho chó mùa đông", "quần áo cho chó nhỏ", "dây dắt chó đi dạo an toàn",
    "chó bị hôi miệng", "đánh răng cho chó", "mèo bị nha chu", "lấy cao răng cho chó", "xịt thơm miệng chó mèo",
    "chó hay liếm chân", "mèo cắn đuôi chảy máu", "chó cắn gót chân chủ", "mèo ngủ nhiều", "chó bị trầm cảm"
]

# Đảm bảo đủ 100 từ khóa
all_keywords = {}
for i, topic in enumerate(topics):
    kw = f"{topic}"
    insights = [
        f"Góc nhìn từ chuyên gia thú y về nguyên nhân sâu xa của {topic}",
        f"Giải pháp điều trị {topic} an toàn bằng phương pháp hữu cơ tại nhà",
        f"Sai lầm phổ biến của người nuôi khi xử lý {topic} và hậu quả",
        f"Hướng dẫn từng bước cách phòng ngừa {topic} hiệu quả",
        f"Câu chuyện thực tế từ chủ nuôi đã chữa khỏi {topic} nhờ sản phẩm Ecopets",
        f"So sánh chi phí khi điều trị {topic} tại thú y và tự chăm sóc đúng cách",
        f"Ảnh hưởng của {topic} đến tâm lý và hành vi của thú cưng",
        f"Phân tích các thành phần độc hại trong thuốc trị {topic} trên thị trường",
        f"Tại sao phương pháp dân gian trị {topic} lại nguy hiểm?",
        f"Cập nhật nghiên cứu mới nhất về {topic} năm 2024"
    ]
    all_keywords[kw] = insights

with open("keyword_clusters.json", "w", encoding="utf-8") as f:
    json.dump(all_keywords, f, ensure_ascii=False, indent=4)

print(f"Đã tạo keyword_clusters.json với {len(all_keywords)} từ khóa.")
