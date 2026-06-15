import json
import os
import time
import pandas as pd
import google.generativeai as genai

# Cấu hình API Key của Gemini (tìm thấy từ project của bạn)
# Nếu bạn muốn đổi key khác, hãy tạo file .env trong thư mục này và điền GEMINI_API_KEY=xxx
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCLUY2lWALBmJW_pZRiW4mKhHhfTz_2M2U")
genai.configure(api_key=API_KEY)

def analyze_with_ai(customer_name, chat_text):
    # Khởi tạo model Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Bạn là một Chuyên gia phân tích tâm lý khách hàng và Cố vấn Sales B2B cấp cao tại Ecopets. 
    Nhiệm vụ của bạn là đọc lịch sử đoạn chat giữa Sale và Đại lý, sau đó phân tích RIÊNG BIỆT TÍNH CÁCH VÀ HÀNH VI CỦA KHÁCH HÀNG CÓ TÊN LÀ: "{customer_name}".
    (Trong nhóm Zalo có nhiều người, nhắc lại, bạn CẦN TẬP TRUNG TỐI ĐA VÀO HÀNH VI, LỜI NÓI CỦA NGƯỜI TÊN: "{customer_name}").

    Dựa vào lịch sử chat dưới đây, hãy xuất ra 1 bản phân tích NGẮN GỌN (khoảng 150-250 chữ) để tóm tắt cho khung Google Sheet:
    1. Tính cách người này: (VD: Nóng tính, chi tiết, hay hỏi giá, quan tâm chất lượng...)
    2. Nỗi đau / Nhu cầu chính: (VD: Cần giao hàng gấp, hay gặp vấn đề hàng hỏng,...)
    3. Hướng tiếp cận tối ưu: (Cách nịnh, cách chăm sóc, đề xuất chốt sale lần tới).

    LỊCH SỬ CHAT:
    {chat_text}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Lỗi khi gọi AI cho khách {customer_name}: {e}")
        return "Lỗi phân tích AI."

def main():
    print("=== BẮT ĐẦU PHÂN TÍCH AI TỰ ĐỘNG KHÁCH HÀNG ===")
    input_file = 'zalo_chat_history_export.json'
    
    if not os.path.exists(input_file):
        print(f"Không tìm thấy {input_file}. Vui lòng chạy tool trích xuất Zalo trước.")
        return
        
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Tải Google Sheet gốc
    sheet_url = "https://docs.google.com/spreadsheets/d/1p6SL8GvM35joTCbKFOz6cvsXNTjyWcutrBq5awn5xw8/export?format=csv"
    try:
        df = pd.read_csv(sheet_url)
    except Exception as e:
        print("Lỗi đọc Google Sheet rồii:", e)
        return
        
    # Đảm bảo có cột Phân tích
    if 'PHÂN TÍCH KHÁCH HÀNG (AI)' not in df.columns:
        df['PHÂN TÍCH KHÁCH HÀNG (AI)'] = ""

    count = 0
    # Duyệt qua từng dòng trong Excel
    for index, row in df.iterrows():
        group_exact_name = row.get('TÊN NHÓM ĐẠI LÝ (CHÍNH XÁC)', '')
        customer_name = row.get('TÊN KHÁCH HÀNG', '')
        
        if pd.isna(group_exact_name) or group_exact_name not in data:
            continue
            
        msgs = data[group_exact_name]
        if not msgs:
            continue
            
        print(f"\nĐang nhờ AI phân tích tính cách cho khách: {customer_name} (Nhóm: {group_exact_name})...")
        
        # Nối tin nhắn
        chat_text = ""
        for m in msgs:
            chat_text += f"[{m.get('time', '')}] {m.get('sender', '')}: {m.get('content', '')}\n"
            
        # Gọi Gemini
        analysis = analyze_with_ai(customer_name, chat_text)
        
        # Lưu thẳng vào DataFrame
        df.at[index, 'PHÂN TÍCH KHÁCH HÀNG (AI)'] = analysis
        count += 1
        
        # Tạm nghỉ 2 giây để tránh kẹt API Rate Limit của Gemini
        time.sleep(2)
        
    # Lưu ra file Excel để người dùng copy
    output_excel = "Ket_Qua_Phan_Tich_AI.xlsx"
    df.to_excel(output_excel, index=False)
    
    print(f"\n[THÀNH CÔNG] Đã phân tích xong {count} khách hàng!")
    print(f"Toàn bộ bảng đã được lưu vào file: {output_excel}")
    print("Bạn chỉ cần mở file này lên, COPY toàn bộ cột PHÂN TÍCH KHÁCH HÀNG (AI) và PASTE thẳng vào link Google Sheet của bạn là xong!")

if __name__ == '__main__':
    main()
