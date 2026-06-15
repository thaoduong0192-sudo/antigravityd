import json
import os

def main():
    input_file = 'zalo_chat_history_export.json'
    output_dir = 'AI_Prompts'
    
    if not os.path.exists(input_file):
        print(f"Không tìm thấy {input_file}. Vui lòng chạy tool trích xuất Zalo trước.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    with open('PROMPT_PHAN_TICH_KHACH_HANG.md', 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    count = 0
    for group, msgs in data.items():
        if not msgs:
            continue
            
        # Nối tin nhắn thành đoạn chat dễ đọc
        chat_text = ""
        for m in msgs:
            time_str = m.get('time', '')
            sender = m.get('sender', '')
            content = m.get('content', '').replace('\n', ' ')
            chat_text += f"[{time_str}] {sender}: {content}\n"
            
        # Tạo file prompt hoàn chỉnh cho đại lý này
        safe_name = "".join([c for c in group if c.isalnum() or c in (' ', '-', '_')]).rstrip()
        file_path = os.path.join(output_dir, f"{safe_name}_Prompt.txt")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(system_prompt)
            f.write("\n\nLỊCH SỬ CHAT CẦN PHÂN TÍCH:\n")
            f.write(chat_text)
            
        count += 1
        
    print(f"Đã tạo thành công {count} file text chứa Prompt AI trong thư mục 'AI_Prompts'.")
    print("Bạn có thể copy nội dung các file này dán vào ChatGPT/Gemini/Claude để ra phân tích chuyên sâu nhất!")

if __name__ == '__main__':
    main()
