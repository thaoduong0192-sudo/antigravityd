import json
import google.generativeai as genai

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# Cấu hình Gemini
genai.configure(api_key=config.get("gemini_api_key", ""))

# Cấu hình model
generation_config = {
  "temperature": 0.8,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 80,
}

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                              generation_config=generation_config)

def generate_comment(channel_name, caption=""):
    context = f"Kênh TikTok: '{channel_name}'"
    if caption:
        context += f"\nMô tả/Caption của video: {caption}"
        
    prompt = f"""
{context}

Viết một bình luận thật ngắn gọn, tự nhiên và ngẫu nhiên bằng tiếng Việt để bình luận dưới video này.
Yêu cầu:
- Đóng vai một người dùng thật, khách hàng thật đang quan tâm hoặc đã dùng sản phẩm.
- Tùy ngữ cảnh caption mà có thể hỏi đáp ("có ai dùng sp này chưa", "dùng như thế nào", "giá sao shop", "xin link mua"), hoặc khen ngợi ("đã dùng rồi oke lắm", "hàng xịn nha", "đỉnh quá").
- Viết như nhắn tin thật, không giống văn mẫu. Thỉnh thoảng dùng teencode nhẹ hoặc sai chính tả 1 chút xíu cho tự nhiên.
- Chỉ trả về đúng nội dung bình luận, tuyệt đối không giải thích, không dùng ngoặc kép bọc lại.
"""
    
    try:
        response = model.generate_content([
            "Bạn là một người dùng mạng xã hội TikTok bình thường ở Việt Nam, đang lướt TikTok và đi comment dạo.",
            prompt
        ])
        comment = response.text.strip().strip('"').strip("'")
        return comment
    except Exception as e:
        print(f"Lỗi khi gọi Gemini API: {e}")
        return "Video hay quá bạn ơi!" # Trả về bình luận mặc định nếu lỗi API

if __name__ == "__main__":
    # Test thử
    print("Test AI:", generate_comment("vtv24news"))
