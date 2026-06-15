import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 41 Models extracted from the user's Model Studio screenshot
MODELS_LIST = [
    "qwen3.5-122b-a10b",
    "qwen3-vl-235b-a22b-thinking",
    "qwen3-max",
    "qwen3.5-plus-2026-02-15",
    "qwen3-235b-a22b-thinking-2507",
    "qwen3-vl-30b-a3b-thinking",
    "qwen3.6-plus",
    "qwen3.6-max-preview",
    "qwen3-32b",
    "qwen3.5-397b-a17b",
    "qwen3.6-flash",
    "qwen3-vl-plus-2025-09-23",
    "qwen3-coder-next",
    "qwen3.5-flash",
    "qwen3.5-35b-a3b",
    "qwen3-30b-a3b-thinking-2507",
    "qwen3-coder-plus-2025-09-23",
    "qwen3-coder-480b-a35b-instruct",
    "qwen3-max-2026-01-23",
    "qwen3-vl-8b-thinking",
    "qwen3-coder-plus",
    "qwen3-vl-flash-2026-01-22",
    "qwen3-vl-flash-2025-10-15",
    "qwen3-max-preview",
    "qwen3.5-flash-2026-02-23",
    "qwen3.7-max-2026-05-20",
    "qwen3-vl-30b-a3b-instruct",
    "qwen3-vl-235b-a22b-instruct",
    "qwen3-coder-30b-a3b-instruct",
    "qwen3-8b",
    "qwen3.6-27b",
    "qwen3-235b-a22b",
    "qwen3-0.5b",
    "qwen3.6-flash-2026-01-16",
    "qwen3-coder-flash",
    "qwen3-vl-plus",
    "qwen3-next-80b-a3b-thinking",
    "qwen3.5-27b",
    "qwen3-30b-a3b",
    "qwen3-vl-flash",
    "qwen-plus-2025-09-11"
]

TOKEN_LIMIT = 950000 # Switch to the next model when usage exceeds 950,000 tokens (safe margin below 1M)
USAGE_FILE = "qwen_usage.json"
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

# Initialize client
client = OpenAI(
    api_key=QWEN_API_KEY,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    # Initialize state
    return {
        "current_model_index": 0,
        "models_usage": {m: 0 for m in MODELS_LIST}
    }

def save_usage(state):
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

def get_current_model(state):
    idx = state.get("current_model_index", 0)
    if idx >= len(MODELS_LIST):
        print("  [!] Đã hết tất cả model Qwen trong danh sách (Rotator exhausted!). Quay lại từ đầu...")
        state["current_model_index"] = 0
        idx = 0
    return MODELS_LIST[idx]

def rotate_model(state):
    state["current_model_index"] += 1
    if state["current_model_index"] >= len(MODELS_LIST):
        state["current_model_index"] = 0 # Loop back
    new_model = MODELS_LIST[state["current_model_index"]]
    print(f"  [🔄] Rotator: Đã đổi sang model mới: {new_model}")
    save_usage(state)
    return new_model

def chat_with_qwen_rotated(prompt, max_tokens=4000, temperature=0.7):
    if not QWEN_API_KEY:
        print("  [-] Lỗi: Không tìm thấy QWEN_API_KEY trong biến môi trường.")
        return None

    state = load_usage()
    model_name = get_current_model(state)
    usage = state["models_usage"].get(model_name, 0)
    
    if usage > TOKEN_LIMIT:
        print(f"  [!] Model {model_name} đã vượt ngưỡng an toàn ({usage} tokens). Tiến hành xoay tua...")
        model_name = rotate_model(state)
        
    print(f"  [AI] Đang gọi model: {model_name} (Đã dùng: {state['models_usage'].get(model_name, 0)}/1,000,000 tokens)")
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a top-tier SEO specialist, veterinarian, and content writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Calculate tokens
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = prompt_tokens + completion_tokens
        
        # Update state
        state["models_usage"][model_name] = state["models_usage"].get(model_name, 0) + total_tokens
        save_usage(state)
        
        print(f"  [AI] Hoàn thành. Đã tiêu thụ {total_tokens} tokens.")
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"  [-] Lỗi Rotator với model {model_name}: {e}")
        # If model is unavailable or throws a quota error, automatically rotate to the next one
        if "quota" in str(e).lower() or "not exist" in str(e).lower() or "invalid" in str(e).lower() or "400" in str(e).lower() or "404" in str(e).lower():
            print(f"  [!] Model {model_name} có vẻ bị lỗi/hết hạn quota. Tự động chuyển model...")
            # Mark it as exhausted to avoid reusing
            state["models_usage"][model_name] = 1000000 
            rotate_model(state)
            # Recursively try again with the new model
            return chat_with_qwen_rotated(prompt, max_tokens, temperature)
            
        return None
