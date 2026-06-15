import uiautomation as auto
import time
import pyperclip
import pandas as pd
import json
import re
import os
from datetime import datetime

class ZaloScraper:
    def __init__(self):
        # Đặt thời gian chờ để các control load
        auto.uiautomation.SetGlobalSearchTimeout(5)
        self.zalo_win = None

    def find_zalo_window(self):
        print("Đang tìm cửa sổ Zalo PC...")
        # Tìm theo ClassName chuẩn của Zalo PC trước
        win_by_class = auto.WindowControl(searchDepth=1, ClassName='ZaloMainWnd')
        if win_by_class.Exists(0, 0):
            self.zalo_win = win_by_class
            print("Đã tìm thấy cửa sổ Zalo (ClassName='ZaloMainWnd')")
            return True
            
        # Nếu không thấy, tìm chính xác tên Zalo (chứ không tìm chứa từ khóa "Zalo" để tránh dính trình duyệt)
        for win in auto.GetRootControl().GetChildren():
            # Zalo PC thường có tên đúng bằng chữ "Zalo"
            if win.Name == "Zalo":
                self.zalo_win = win
                print(f"Đã tìm thấy cửa sổ: {self.zalo_win.Name}")
                return True
                
        print("Không tìm thấy cửa sổ Zalo. Vui lòng CHẮC CHẮN RẰNG phần mềm Zalo PC đang mở trên màn hình.")
        return False

    def focus_window(self):
        if self.zalo_win:
            try:
                self.zalo_win.SetFocus()
                self.zalo_win.SetActive()
                time.sleep(1)
            except Exception as e:
                print(f"Lỗi focus: {e}")

    def search_and_open_group(self, group_name):
        print(f"Đang tìm nhóm: {group_name}")
        self.focus_window()
        
        # Thử kích hoạt ô tìm kiếm. Zalo thường hỗ trợ phím tắt Ctrl+F để tìm liên hệ
        self.zalo_win.SendKeys('{Ctrl}f')
        time.sleep(1)
        
        # Xóa text cũ nếu có
        self.zalo_win.SendKeys('{Ctrl}a{Delete}')
        time.sleep(0.5)
        
        # Gõ tên nhóm
        pyperclip.copy(group_name)
        self.zalo_win.SendKeys('{Ctrl}v')
        time.sleep(2) # Đợi Zalo filter kết quả
        
        # Bấm Enter để chọn kết quả đầu tiên (thường là group đúng nhất vì tìm theo Group ID hoặc tên chính xác)
        self.zalo_win.SendKeys('{Enter}')
        time.sleep(2) # Đợi load tin nhắn

    def extract_messages(self, scroll_times=5):
        print(f"Đang trích xuất tin nhắn... Cuộn {scroll_times} lần.")
        self.focus_window()
        
        # Click vào vùng chat panel (để đảm bảo focus vào area tin nhắn trước khi cuộn/copy)
        # Tab một vài lần hoặc click giữa màn hình
        chat_pane = self.zalo_win.BoundingRectangle
        center_x = (chat_pane.left + chat_pane.right) // 2
        center_y = (chat_pane.top + chat_pane.bottom) // 2
        auto.Click(center_x, center_y)
        time.sleep(0.5)

        # Cuộn lên để load lịch sử
        for i in range(scroll_times):
            auto.WheelUp(wheelTimes=10)
            time.sleep(1) # Chờ mạng load tin nhắn cũ

        # Copy tất cả tin nhắn
        pyperclip.copy('') # Xóa clipboard
        self.zalo_win.SendKeys('{Ctrl}a')
        time.sleep(0.5)
        self.zalo_win.SendKeys('{Ctrl}c')
        time.sleep(1)
        
        # Lấy text
        chat_text = pyperclip.paste()
        self.zalo_win.SendKeys('{Esc}') # Bỏ chọn bôi đen
        
        return self.parse_chat_text(chat_text)

    def parse_chat_text(self, text):
        """
        Phân tích text thô từ việc copy Ctrl+C của Zalo thành cấu trúc.
        Định dạng copy của Zalo thường có dạng:
        [Tên]  [Giờ:Phút]
        [Nội dung]
        [Nội dung dòng 2]
        """
        lines = text.split('\n')
        messages = []
        current_msg = None
        
        # Thường tên và giờ cách nhau một lúc
        # Regex tìm dòng có giờ (VD: 10:25 hoặc 10:25 Hôm nay)
        time_pattern = re.compile(r'(\d{1,2}:\d{2})')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Kiểm tra xem dòng này có phải là header (Tên + Giờ) không
            match = time_pattern.search(line)
            if match and len(line) < 50: # Dòng độ dài ngắn chứa time thường là header
                time_str = match.group(1)
                sender = line.replace(time_str, '').strip()
                # Có thể Zalo copy thêm chữ 'Hôm nay', 'Thứ 2', v.v. bỏ qua
                sender = re.sub(r'(Hôm nay|Hôm qua|Thứ \w+|Ngày \d+/\d+)', '', sender).strip()
                
                if current_msg:
                    messages.append(current_msg)
                    
                current_msg = {
                    "sender": sender,
                    "time": time_str,
                    "content": ""
                }
            else:
                if current_msg:
                    if current_msg["content"]:
                        current_msg["content"] += "\n" + line
                    else:
                        current_msg["content"] = line
                else:
                    # Nếu chưa có header, có thể là dòng ngày tháng phân cách hoặc rác
                    pass
                    
        if current_msg:
            messages.append(current_msg)
            
        return messages

def main():
    print("=== Khởi động Tool Trích xuất Zalo PC ===")
    
    # Đọc danh sách file trực tiếp từ Google Sheet để tránh lỗi font chữ Excel và lấy Toàn bộ danh sách
    sheet_url = "https://docs.google.com/spreadsheets/d/1p6SL8GvM35joTCbKFOz6cvsXNTjyWcutrBq5awn5xw8/export?format=csv"
    print(f"Đang tải danh sách đại lý từ Google Sheet: {sheet_url}")
    
    try:
        df = pd.read_csv(sheet_url)
    except Exception as e:
        print(f"LỖI: Không thể tải dữ liệu từ Google Sheet. Chi tiết: {e}")
        return
        
    if 'TÊN NHÓM ĐẠI LÝ (CHÍNH XÁC)' not in df.columns:
        print("LỖI: Trạng tính thiếu cột 'TÊN NHÓM ĐẠI LÝ (CHÍNH XÁC)'.")
        return
        
    target_groups = df['TÊN NHÓM ĐẠI LÝ (CHÍNH XÁC)'].dropna().tolist()
    print(f"Đã tìm thấy {len(target_groups)} nhóm đại lý cần trích xuất.")
    
    scraper = ZaloScraper()
    if not scraper.find_zalo_window():
        return
        
    output_file = 'zalo_chat_history_export.json'
    
    # Load data cũ nếu có để chạy tiếp (resume)
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    else:
        all_data = {}
    
    for group in target_groups:
        if group in all_data and len(all_data[group]) > 0:
            print(f"Bỏ qua (đã cào): {group}")
            continue
            
        scraper.search_and_open_group(group)
        # Cuộn 15 lần để lấy khoảng 1-2 tháng lịch sử trò chuyện
        msgs = scraper.extract_messages(scroll_times=15)
        all_data[group] = msgs
        
        print(f"Đã lấy {len(msgs)} tin nhắn từ nhóm: {group}")
        
        # Lưu file JSON ngay lập tức sau mỗi nhóm để lỡ tool dừng giữa chừng vẫn không mất dữ liệu
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
            
        time.sleep(2)
        
    print(f"\n[THÀNH CÔNG] Đã lưu dữ liệu {len(all_data)} nhóm vào {output_file}")

if __name__ == '__main__':
    main()
