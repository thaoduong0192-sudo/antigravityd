import subprocess
import json
import sys
import time
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_cmd(cmd, capture=True):
    try:
        res = subprocess.run(
            cmd, check=True, capture_output=capture, text=True, encoding='utf-8'
        )
        return res.stdout if capture else None
    except subprocess.CalledProcessError as e:
        print(f"[LỖI] Lệnh thất bại: {' '.join(cmd)}")
        if e.stderr:
            print(e.stderr)
        elif e.stdout:
            print(e.stdout)
        raise e

def main():
    if len(sys.argv) < 2:
        print("Vui lòng truyền vào chủ đề khóa học.")
        sys.exit(1)
        
    topic = sys.argv[1]
    title = f"Khóa Học: {topic}"
    
    # Bước 1: Tạo Notebook
    print(f"1. Đang tạo Sổ ghi chú mới: {title}...")
    try:
        out = run_cmd(["uv", "run", "nlm", "notebook", "create", title, "--json"])
        nb_data = json.loads(out)
        nb_id = nb_data.get("notebook_id")
        nb_url = nb_data.get("url")
    except Exception as e:
        print("Không thể tạo Notebook hoặc parse JSON:", e)
        sys.exit(1)
        
    print(f"   => Thành công! Notebook ID: {nb_id}")
    
    # Bước 2: Nạp 50 URLs
    print("2. Đang nạp danh sách 50 video từ urls.txt...")
    try:
        with open("urls.txt", "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception:
        print("Không tìm thấy file urls.txt")
        sys.exit(1)
        
    for i, url in enumerate(urls, 1):
        print(f"   [{i}/{len(urls)}] Nạp {url}...")
        try:
            subprocess.run(["uv", "run", "nlm", "source", "add", nb_id, "--url", url], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode('utf-8') if e.stderr and isinstance(e.stderr, bytes) else str(e)
            print(f"   -> Lỗi bỏ qua: {err}")
            # Nếu dính lỗi auth, dừng lại luôn để báo người dùng
            if "Authentication expired" in err or "unauthorized" in err.lower():
                print("LỖI XÁC THỰC! Vui lòng mở terminal gõ `nlm login` lại.")
                sys.exit(1)
        time.sleep(0.5)
        
    # Bước 3: Truy vấn 20 chủ đề
    print("3. Đang yêu cầu AI phân tích và xuất 20 chủ đề con...")
    outline_prompt = (
        "Dựa vào các nguồn, hãy thiết kế một khóa học chuyên sâu gồm chính xác 20 chủ đề con. "
        "Yêu cầu TRẢ VỀ CHỈ MỘT MẢNG JSON hợp lệ chứa 20 chuỗi là tên của 20 chủ đề con. "
        "Ví dụ: [\"Chủ đề 1\", \"Chủ đề 2\", ...]. Không giải thích gì thêm."
    )
    
    try:
        out = run_cmd(["uv", "run", "nlm", "notebook", "query", nb_id, outline_prompt, "--json"])
        query_data = json.loads(out)
        answer_text = query_data.get("answer", out)
        
        # Tìm đoạn bọc bởi [] trong answer_text
        match = re.search(r'\[\s*".*\]', answer_text, re.DOTALL)
        if match:
            topics = json.loads(match.group(0))
        else:
            topics = json.loads(answer_text)
    except Exception as e:
        print("Lỗi parse JSON 20 chủ đề:", e)
        print("Kết quả thô:", out)
        sys.exit(1)
        
    if not topics or not isinstance(topics, list):
        print("Không lấy được danh sách chủ đề!")
        sys.exit(1)
        
    # Chuẩn hóa để lấy đúng 20 chủ đề
    topics = [str(t).strip() for t in topics][:20]
    print(f"   => Đã tìm thấy {len(topics)} chủ đề con!")
    
    # Bước 4: Vòng lặp 20 lần
    for idx, sub_topic in enumerate(topics, 1):
        print(f"\n--- Xử lý Bài {idx}/20: {sub_topic} ---")
        
        try:
            # Sinh nội dung Ghi chú
            print(f"  a. Đang sinh nội dung Ghi chú...")
            prompt_note = (
                f"Hãy đóng vai một chuyên gia, soạn một bài giảng thật chi tiết về chủ đề: '{sub_topic}'. "
                "Cấu trúc: 40% Lý thuyết, 30% Ví dụ thực tế, 30% Bài tập thực hành. "
                "Chỉ dựa vào các nguồn đã cung cấp. "
                "YÊU CẦU BẮT BUỘC: Toàn bộ nội dung trả về phải được viết 100% bằng Tiếng Việt (Vietnamese)."
            )
            run_cmd(["uv", "run", "nlm", "notebook", "query", nb_id, prompt_note, "--json"])
            
            # Gọi chats to-note
            print(f"  b. Đang lưu vào Ghi chú...")
            chat_list_out = run_cmd(["uv", "run", "nlm", "chats", "list", nb_id, "--json"])
            chat_data = json.loads(chat_list_out)
            conv_id = chat_data["sessions"][0]["conversation_id"]
            run_cmd(["uv", "run", "nlm", "chats", "to-note", nb_id, conv_id, "--json"])
            
            # Ra lệnh render Video với --focus và --language vi
            print(f"  c. Ra lệnh render Video bài giảng tập trung vào: '{sub_topic}'...")
            focus_arg = f"Bài {idx}: {sub_topic}. YÊU CẦU ĐẶC BIỆT: Âm thanh và văn bản trong video PHẢI BẰNG TIẾNG VIỆT (Vietnamese) 100%."
            run_cmd(["uv", "run", "nlm", "video", "create", nb_id, "--format", "explainer", "--focus", focus_arg, "--language", "vi", "--confirm", "--json"])
            
            # Nghỉ xíu tránh spam server
            time.sleep(3)
        except Exception as e:
            print(f"  -> Lỗi trong quá trình xử lý bài {idx}: {e}")
            if "Authentication expired" in str(e):
                print("LỖI XÁC THỰC! Vui lòng mở terminal gõ `nlm login` lại.")
                sys.exit(1)
            print("  -> Bỏ qua và tiếp tục bài tiếp theo...")
        
    print("\n=============================================")
    print(f"HOÀN TẤT TẠO KHÓA HỌC {len(topics)} BÀI!")
    print(f"Link NotebookLM của bạn: {nb_url}")
    print("Tất cả Video đang được render ngầm trên server Google.")
    print("=============================================")

if __name__ == "__main__":
    main()
