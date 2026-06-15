import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

_CANDIDATE_ENDPOINTS = [
    ("https://dashscope-intl.aliyuncs.com/compatible-mode/v1", "qwen-plus-latest"),
    ("https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-plus-latest"),
    ("https://openrouter.ai/api/v1", "qwen/qwen-plus"),
]

def _detect_working_client(api_key):
    if not api_key: return None, None
    for base_url, model in _CANDIDATE_ENDPOINTS:
        try:
            client = OpenAI(api_key=api_key, base_url=base_url)
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            if resp.choices: return client, model
        except: pass
    return None, None

client, model = _detect_working_client(QWEN_API_KEY)

CATEGORIES = [
    "bọt vệ sinh tai chó mèo, trị viêm tai",
    "canxi hữu cơ chó mèo, ngừa sỏi thận",
    "beta amin chó mèo, phục hồi sức khỏe",
    "xịt khử khuẩn, nấm da, rụng lông",
    "men vi sinh, tiêu chảy, viêm ruột",
    "bệnh thường gặp ở chó",
    "bệnh thường gặp ở mèo",
    "sữa tắm khô, khử mùi chó mèo",
    "chăm sóc chó mèo mang thai",
    "dinh dưỡng chó mèo theo độ tuổi"
]

all_data = {}

def get_keywords_for_category(cat):
    prompt = f"""Tạo danh sách 10 TỪ KHÓA TÌM KIẾM (keywords) dài và chi tiết của người nuôi thú cưng tại Việt Nam về chủ đề: "{cat}".
Trả về ĐÚNG MỘT danh sách mảng JSON (chỉ có mảng, không markdown, không giải thích), ví dụ:
[
  "cách chữa chó bị nôn mửa bọt trắng tại nhà",
  "mèo bị rụng lông quanh cổ phải làm sao"
]
"""
    try:
        res = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1000)
        content = res.choices[0].message.content.strip()
        if "```json" in content: content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content: content = content.split("```")[1].strip()
        return json.loads(content)
    except Exception as e:
        print("Lỗi khi sinh keywords cho", cat, e)
        return []

def get_insights_for_keyword(kw):
    prompt = f"""Sinh ra 10 'Insights' (góc nhìn độc đáo, tình huống thực tế, góc nhìn phân tích sâu) cho chủ đề viết bài: "{kw}".
Ví dụ Insight: "Góc nhìn từ chủ nuôi chó có thú cưng bị nấm da mãn tính - ảnh hưởng tới tâm lý gia đình".
Trả về ĐÚNG MỘT danh sách mảng JSON chứa các chuỗi (không markdown).
"""
    try:
        res = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=2000)
        content = res.choices[0].message.content.strip()
        if "```json" in content: content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content: content = content.split("```")[1].strip()
        return json.loads(content)
    except:
        return [f"Insight phân tích sâu về nguyên nhân cốt lõi của {kw}", f"Hướng dẫn thực tế từng bước xử lý {kw}", f"So sánh các phương pháp điều trị {kw}"]

print("Bắt đầu sinh keyword_clusters.json cho Ecopets...")
for cat in CATEGORIES:
    print(f"Đang sinh từ khóa cho nhóm: {cat}")
    kws = get_keywords_for_category(cat)
    for kw in kws:
        if len(all_data) >= 100: break
        insights = get_insights_for_keyword(kw)
        all_data[kw] = insights
        print(f" + {kw} ({len(insights)} insights)")
    if len(all_data) >= 100: break

with open("keyword_clusters.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)
print(f"Xong! Đã lưu {len(all_data)} từ khóa vào keyword_clusters.json")
