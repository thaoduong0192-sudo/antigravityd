import csv
import os
from datetime import datetime

def log_interaction(account_idx, channel_name, action, details=""):
    """
    Ghi log các tương tác thành công vào file CSV theo ngày.
    """
    os.makedirs('logs', exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join('logs', f'report_{today}.csv')
    
    file_exists = os.path.exists(file_path)
    
    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Thời gian', 'Tài khoản', 'Kênh tương tác', 'Hành động', 'Chi tiết'])
            
        now = datetime.now().strftime('%H:%M:%S')
        writer.writerow([now, f"Tài khoản {account_idx}", channel_name, action, details])

def generate_daily_summary():
    """
    Hàm hỗ trợ đọc file log hôm nay và in ra thống kê tổng quan.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join('logs', f'report_{today}.csv')
    
    if not os.path.exists(file_path):
        return f"Chưa có dữ liệu chạy cho ngày {today}."
        
    likes = 0
    shares = 0
    comments = 0
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            action = row.get('Hành động', '')
            if action == 'Like':
                likes += 1
            elif action == 'Share':
                shares += 1
            elif action == 'Comment':
                comments += 1
                
    summary = f"--- BÁO CÁO NHANH NGÀY {today} ---\n"
    summary += f"- Tổng số lượt Like: {likes}\n"
    summary += f"- Tổng số lượt Share: {shares}\n"
    summary += f"- Tổng số lượt Comment: {comments}\n"
    summary += f"Chi tiết xem tại file: {file_path}"
    
    return summary

if __name__ == "__main__":
    print(generate_daily_summary())
