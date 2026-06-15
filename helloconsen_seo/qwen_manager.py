import os
import json
import time
import random
from openai import OpenAI
from dotenv import load_dotenv
import google.generativeai as genai

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(DIR_PATH, ".env"))
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
    os.getenv("GEMINI_API_KEY_5"),
    os.getenv("GEMINI_API_KEY_6")
]
GEMINI_KEYS = [k for k in GEMINI_KEYS if k]

FREE_MODELS = [
    "qwen-max",
    "qwen3-max-preview",
    "qwen3.7-max-preview",
    "qwen3.5-flash",
    "qwen3.6-flash",
    "qwen3-coder-plus",
    "deepseek-v3.2",
    "deepseek-v4-flash",
    "deepseek-v4-pro",
    "qwen3-coder-next",
    "qwen3-max-2026-01-23",
    "qwen3.7-max-2026-05-17",
    "qwen3-next-80b-a3b-thinking",
    "qwen-mt-flash",
    "qwen3.5-55b-a3b",
    "qwen3-30b-a3b",
    "qwen3.6-27b",
    "qwen3.5-27b",
    "qwen3-14b"
]

MAX_FREE_TOKENS = 950000  # Ngưỡng an toàn (95%)
TRACKER_FILE = "D:\\Antigravity\\qwen_token_usage.json"

def load_token_usage():
    if not os.path.exists(TRACKER_FILE):
        usage = {model: 0 for model in FREE_MODELS}
        save_token_usage(usage)
        return usage
    try:
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {model: 0 for model in FREE_MODELS}

def save_token_usage(usage):
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(usage, f, indent=4)

def chat_with_gemini(prompt, temperature):
    print("  [AI] Đang chuyển hướng sang Gemini 1.5 Flash (Backup do Qwen hết Quota)...")
    if not GEMINI_KEYS:
        print("  [-] Không tìm thấy Gemini API Key nào trong .env!")
        return None
        
    random.shuffle(GEMINI_KEYS) # Rotate keys
    for key in GEMINI_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                )
            )
            print("  [AI] Đã nhận kết quả từ Gemini thành công!")
            return response.text
        except Exception as e:
            print(f"  [-] Lỗi Gemini (Key {key[-4:]}): {e}")
            time.sleep(2)
            
    print("  [-] TẤT CẢ CÁC KEY GEMINI ĐỀU LỖI!")
    return None

def chat_with_qwen(prompt, max_tokens=8000, temperature=0.8):
    usage = load_token_usage()
    
    for model in FREE_MODELS:
        if usage.get(model, 0) >= MAX_FREE_TOKENS:
            continue
            
        print(f"  [AI] Đang gọi model free: {model} (Đã dùng: {usage.get(model, 0):,}/1,000,000 tokens)")
        
        try:
            client = OpenAI(
                api_key=QWEN_API_KEY, 
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
            )
            
            request_tokens = max_tokens
            if model == "qwen-plus-character":
                request_tokens = min(request_tokens, 4096)
                
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=request_tokens,
                temperature=temperature
            )
            
            raw = resp.choices[0].message.content.strip()
            
            if hasattr(resp, 'usage') and resp.usage:
                tokens_used = resp.usage.total_tokens
                usage[model] = usage.get(model, 0) + tokens_used
                save_token_usage(usage)
                print(f"  [AI] Đã cộng thêm {tokens_used} tokens vào {model}.")
            
            return raw
            
        except Exception as e:
            error_str = str(e)
            print(f"  [-] Lỗi với model {model}: {error_str}")
            if "AllocationQuota.FreeTierOnly" in error_str or "quota" in error_str.lower():
                usage[model] = 1000000  # Đánh dấu đã hết hạn mức
                save_token_usage(usage)
                print(f"  [AI] Model {model} đã hết Free Quota. Tự động chuyển sang model tiếp theo...")
                continue
            else:
                print(f"  [AI] Thử chuyển sang model tiếp theo do lỗi không xác định...")
                time.sleep(2)
                continue
                
    print("[-] TẤT CẢ 6 TRIỆU TOKEN CỦA CÁC MODEL FREE QWEN ĐỀU ĐÃ HẾT HOẶC BỊ LỖI!")
    
    # Hết quota Qwen thì Fallback sang Gemini
    return chat_with_gemini(prompt, temperature)
