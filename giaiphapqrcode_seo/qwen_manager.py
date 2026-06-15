import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

FREE_MODELS = [
    "qwen-plus-latest",
    "qwen-plus-2025-07-28",
    "qwen-plus-2025-09-11",
    "qwen-plus-character",
    "qwen-plus-2025-04-28",
    "qwen-plus-2025-07-14"
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
            
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
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
                return None
                
    print("[-] TẤT CẢ 6 TRIỆU TOKEN CỦA CÁC MODEL FREE ĐỀU ĐÃ HẾT HOẶC BỊ LỖI!")
    return None
