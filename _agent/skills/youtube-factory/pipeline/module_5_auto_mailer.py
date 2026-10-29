import os
import re
import smtplib
import imaplib
import email as email_lib
import json
import time
import sys
from email.message import EmailMessage
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") # App Password
USER_DATA_DIR = os.path.abspath("chrome_profile_bot")

SENT_EMAILS_FILE = "output_factory/sent_emails.txt"
EBOOK_PATH = "output_factory/ebook/Giao_Trinh_Antigravity_Cap2.pdf"
MOCK_COMMENTS_FILE = "mock_youtube_comments.json"

def get_sent_emails():
    if not os.path.exists(SENT_EMAILS_FILE):
        os.makedirs(os.path.dirname(SENT_EMAILS_FILE), exist_ok=True)
        return set()
    with open(SENT_EMAILS_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())

def save_sent_email(to_email):
    os.makedirs(os.path.dirname(SENT_EMAILS_FILE), exist_ok=True)
    with open(SENT_EMAILS_FILE, 'a', encoding='utf-8') as f:
        f.write(to_email.lower() + '\n')

def extract_emails(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)

def send_ebook(to_email):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print(f"  [!] LỖI: Chưa cấu hình EMAIL_SENDER hoặc EMAIL_PASSWORD trong .env. Bỏ qua {to_email}.")
        return False

    if not os.path.exists(EBOOK_PATH):
        print(f"  [!] LỖI: Không tìm thấy file Ebook tại {EBOOK_PATH}")
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = 'Tặng bạn: E-Book Giáo trình Vibe Code Antigravity'
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        
        body = '''Chào bạn,

Cảm ơn bạn đã xem video và quan tâm đến kênh!
Như đã hứa, mình gửi tặng bạn E-Book "Giáo trình Thiết kế vibe code bằng antigravity đơn giản cho học sinh cấp 2" trong file đính kèm.

Chúc bạn học tập thật tốt và tự tay tạo ra được những ứng dụng tuyệt vời!

Trân trọng,
Hệ thống Auto-Mailer Antigravity
'''
        msg.set_content(body)
        
        with open(EBOOK_PATH, 'rb') as f:
            pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=os.path.basename(EBOOK_PATH))
            
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            
        print(f"  [✓] ĐÃ GỬI EBOOK THÀNH CÔNG TỚI: {to_email}")
        return True
    except Exception as e:
        print(f"  [!] Lỗi khi gửi email tới {to_email}: {e}")
        return False

def scan_youtube_studio_comments(sent_emails):
    """ Mở YouTube Studio qua Playwright và quét tất cả Bình luận thực tế """
    print("\n[*] Đang quét bình luận thực tế trên YouTube Studio...")
    found_emails = set()
    
    if not os.path.exists(USER_DATA_DIR):
        print("  [!] Không tìm thấy Chrome Profile. Bỏ qua quét Studio.")
        return found_emails

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = browser.new_page()
            page.goto("https://studio.youtube.com")
            time.sleep(5)
            
            # Chuyển trực tiếp sang trang Bình luận của kênh
            try:
                page.goto("https://studio.youtube.com/channel/comments")
                time.sleep(5)
            except:
                pass
                
            # Trích xuất toàn bộ innerText của body trang comments
            body_text = page.locator("body").inner_text()
            extracted = extract_emails(body_text)
            for e in extracted:
                found_emails.add(e.lower())
                
            print(f"  + Đã quét thấy {len(extracted)} email trong bình luận YouTube Studio.")
            browser.close()
    except Exception as e:
        print(f"  [!] Lỗi khi quét bình luận YouTube Studio: {e}")
        
    return found_emails

def scan_gmail_inbox(sent_emails):
    """ Quét thư đến Gmail (IMAP) để tìm khán giả gửi email xin Ebook """
    print("\n[*] Đang quét Hòm thư Gmail đến (IMAP)...")
    found_emails = set()
    
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return found_emails

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_SENDER, EMAIL_PASSWORD)
        mail.select("inbox")
        
        # Tìm thư chưa đọc hoặc tất cả thư gần đây
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        # Quét 20 thư mới nhất
        for mail_id in email_ids[-20:]:
            status, data = mail.fetch(mail_id, "(RFC822)")
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email_lib.message_from_bytes(response_part[1])
                    from_header = msg.get("From", "")
                    sender_email = extract_emails(from_header)
                    if sender_email:
                        found_emails.add(sender_email[0].lower())
                    
                    # Quét cả nội dung thư nếu khán giả viết email chứa mail khác
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                body = part.get_payload(decode=True).decode(errors='ignore')
                                for e in extract_emails(body):
                                    found_emails.add(e.lower())
                                    
        mail.logout()
    except Exception as e:
        print(f"  [!] Không thể kết nối IMAP Gmail (có thể cần bật IMAP trong Cài đặt Gmail): {e}")
        
    return found_emails

def auto_mailer_job():
    print("=== MODULE 5: YOUTUBE AUTO-MAILER BẮT ĐẦU ===")
    sent_emails = get_sent_emails()
    
    # 1. Quét từ Mock Comments
    mock_emails = set()
    if os.path.exists(MOCK_COMMENTS_FILE):
        with open(MOCK_COMMENTS_FILE, 'r', encoding='utf-8') as f:
            for c in json.load(f):
                for e in extract_emails(c.get('text', '')):
                    mock_emails.add(e.lower())
                    
    # 2. Quét thực tế từ YouTube Studio Comments
    yt_emails = scan_youtube_studio_comments(sent_emails)
    
    # 3. Quét thực tế từ Gmail Inbox
    gmail_emails = scan_gmail_inbox(sent_emails)
    
    all_target_emails = mock_emails.union(yt_emails).union(gmail_emails)
    print(f"\n[*] Tổng số email phát hiện được: {len(all_target_emails)}")
    
    new_count = 0
    for email in all_target_emails:
        if email in sent_emails or email == EMAIL_SENDER.lower():
            continue
            
        print(f"[*] Gửi Ebook tới email mới: {email}")
        if send_ebook(email):
            save_sent_email(email)
            sent_emails.add(email)
            new_count += 1
            time.sleep(2)
            
    print(f"\n[✓] MODULE 5 HOÀN TẤT. Đã gửi thêm cho {new_count} email mới.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Module 5: Auto-Mailer")
    parser.add_argument("--channel-dir", type=str, default="", help="Thư mục xuất dữ liệu kênh")
    parser.add_argument("--topic-dir", type=str, default="", help="Thư mục xuất dữ liệu topic")
    args = parser.parse_args()
    
    if args.channel_dir and os.path.exists(args.channel_dir):
        SENT_EMAILS_FILE = os.path.join(args.channel_dir, "sent_emails.txt")
        custom_ebook = os.path.join(args.channel_dir, "ebook", "Giao_Trinh_Antigravity_Cap2.pdf")
        if os.path.exists(custom_ebook):
            EBOOK_PATH = custom_ebook
            
    if args.topic_dir and os.path.exists(args.topic_dir):
        SENT_EMAILS_FILE = os.path.join(args.topic_dir, "sent_emails.txt")
        custom_ebook = os.path.join(args.topic_dir, "ebook", "Giao_Trinh_Antigravity_Cap2.pdf")
        if os.path.exists(custom_ebook):
            EBOOK_PATH = custom_ebook
            
    auto_mailer_job()
