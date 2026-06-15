import os
import sys
import time
import datetime
import schedule
import pyperclip
import pyautogui
from google import genai

# ================= CẤU HÌNH CƠ BẢN =================
# Thay ĐỔI tên Group Zalo chính xác (hoặc tên người nhận) ở đây
GROUP_NAME = "GIA ĐÌNH CỦA BƯ" 

# Lấy API Key từ biến môi trường của hệ thống
# Nếu chưa có biến môi trường, bạn có thể điền thẳng key vào đây: 
# API_KEY = "AIzaSy..."
API_KEY = "AIzaSyBIg9YifzdXwgm9a1blA3j_xVwUwq7tv00"
# ===================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PROFILE = os.path.join(BASE_DIR, "01_Inputs", "Ho_so_cua_Bu.md")
FILE_REPORT = os.path.join(BASE_DIR, "01_Inputs", "Bao_cao_phat_trien.md")
FILE_HISTORY = os.path.join(BASE_DIR, "03_Outputs", "Lich_su_tro_choi.md")
FILE_SKILL = os.path.join(BASE_DIR, "_agent", "skills", "chuyen-gia-sang-tao-tro-choi-bat-am.md")

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def append_to_history(game_title):
    try:
        with open(FILE_HISTORY, 'a', encoding='utf-8') as f:
            now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            f.write(f"\n- Bật âm {now_str}: {game_title}")
        print(f"Đã cập nhật lịch sử: {game_title}")
    except Exception as e:
        print(f"Lỗi khi ghi lịch sử: {e}")

def create_zalo_message():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Đang kết nối AI để suy nghĩ ý tưởng trò chơi...")
    if not API_KEY:
        print(">> LỖI DỪNG: Không tìm thấy GEMINI_API_KEY. Vui lòng thiết lập biến môi trường!")
        return None
    
    profile = read_file(FILE_PROFILE)
    report = read_file(FILE_REPORT)
    history = read_file(FILE_HISTORY)
    skill_rules = read_file(FILE_SKILL)
    
    current_hour = datetime.datetime.now().hour
    if current_hour in [8, 19] or current_hour >= 18:
        phu_trach = "Ba Mẹ"
    else:
        phu_trach = "Ông Bà Ngoại"

    prompt = f"""
Bạn là Chuyên gia thiết kế trò chơi tự động (15 phút) cho bé Bư.
Dựa vào các dữ liệu hệ thống bên dưới:

1. Hồ sơ của bé:
{profile}

2. Báo cáo Tình trạng gốc:
{report}

3. Lịch sử các trò đã từng chơi 30 ngày qua (TUYỆT ĐỐI KHÔNG LẶP LẠI VÀ CHẾ RA TRÒ HOÀN TOÀN MỚI):
{history}

4. Kỹ năng & Tiêu chuẩn xuất ra:
{skill_rules}

================

NHIỆM VỤ CỦA BẠN LÀ: 
Sinh ra MỘT kịch bản Giao tiếp Tương tác (15 phút) dành cho {phu_trach} chơi với bé Bư trong khung giờ hiện tại ({current_hour}:00).
- Không thêm các câu chào mở đầu hay kết thúc mà tập trung trả thẳng nội dung kịch bản để gửi đi Zalo.
- Ở dòng ĐẦU TIÊN CÙNG của kết quả, hãy dùng cú pháp chứa tên trò chơi. Ví dụ: "🎯 [TÊN TRÒ CHƠI HOẠT ĐỘNG]". Điều này rất quan trọng để hệ thống lập chỉ mục vào lịch sử!
"""
    try:
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f">> Gặp Lỗi gọi Gemini: {e}")
        return None

def send_zalo(text):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Khởi động tay bóp chuột Zalo...")
    
    # 1. Trích xuất tên trò chơi từ dòng đầu tiên
    first_line = text.strip().split('\n')[0][:80]
    append_to_history(first_line)
    
    # 2. Xóa khoảng trắng thừa
    clean_message = text.strip()
    
    # 3. Copy text
    pyperclip.copy(clean_message)
    
    # 4. Giả lập chuột phím
    print(">> Đang bật Zalo...")
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write('Zalo')
    time.sleep(1)
    pyautogui.press('enter')
    
    # Chờ Zalo mở và kết nối mạng (thời gian này tuỳ máy, mình set 3s an toàn)
    time.sleep(3)
    
    print(f">> Đang tìm group '{GROUP_NAME}'...")
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    # Copy tên group paste vào ô search Zalo để lách lỗi bộ gõ tiếng Việt Unikey
    pyperclip.copy(GROUP_NAME)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(2)  # Chờ zalo vớt kết quả tìm kiếm
    pyautogui.press('enter')
    time.sleep(1)
    
    print(">> Đang gửi tin lên Group...")
    # Paste message kịch bản
    pyperclip.copy(clean_message) 
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    print(">> HOÀN TẤT gửi tin Zalo vòng lặp!")

def job():
    print(f"\n======================================")
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Kích hoạt Nhiệm vụ Gửi Giờ Chơi!")
    message = create_zalo_message()
    if message:
        send_zalo(message)
    else:
        print(">> Bỏ qua nhịp này do lỗi lấy nội dung gốc.")

def run_test():
    print("--- CHẾ ĐỘ TEST (Chạy ngay 1 lần) ---")
    job()
    print("--- KẾT THÚC TEST ---")

if __name__ == "__main__":
    print(f"[BOT ZALO] Hệ thống Zalo Bu Agent đã sẵn sàng!")
    print(f"Mục tiêu tìm nhóm: [{GROUP_NAME}]")
    print(f"Lập lịch chạy các mốc: 08:00, 11:00, 15:00, 19:00")
    if API_KEY:
         print(f"API Key Google Gemini: [OK - Đã cấu hình]")
    else:
         print(f"API Key Google Gemini: [CẢNH BÁO - Đang cấu hình rỗng!]")
         
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test()
    else:
        # Lập lịch Automation
        schedule.every().day.at("08:00").do(job)
        schedule.every().day.at("11:00").do(job)
        schedule.every().day.at("15:00").do(job)
        schedule.every().day.at("19:00").do(job)

        while True:
            schedule.run_pending()
            time.sleep(30)
