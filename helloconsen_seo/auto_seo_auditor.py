import os
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL", "https://helloconsen.com")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

WP_POSTS_API = f"{WP_URL}/wp-json/wp/v2/posts"

def evaluate_post(title, content):
    score = 100
    issues = []
    
    # 1. Kiểm tra CLS (Width/Height của Ảnh)
    img_tags = re.findall(r'<img[^>]+>', content)
    for img in img_tags:
        if ' width="' not in img or ' height="' not in img:
            issues.append("Báo động Đỏ: Tìm thấy Hình ảnh thiếu width/height -> Gây nhảy hình CLS")
            score -= 20
            break  # Chỉ trừ 1 lần cho lỗi này
            
    # 2. Kiểm tra Schema (Rich Snippets)
    if 'application/ld+json' not in content:
        issues.append("Cảnh báo: Thiếu Schema Markup JSON-LD -> Tụt hạng E-E-A-T")
        score -= 20
        
    # 3. Kiểm tra Header
    if '<h2' not in content.lower():
        issues.append("Kém: Bài viết không có phân cấp thẻ <h2>")
        score -= 10
        
    # 4. Kiểm tra Internal Link
    if 'href="https://helloconsen.com' not in content and 'href="/' not in content:
        issues.append("Kém: Không tìm thấy Internal Link trỏ về web nhà")
        score -= 10
        
    return score, issues

def run_auditor():
    print("=========================================================")
    print("        AUTO SEO AUDITOR - TRẠM KIỂM ĐỊNH KỸ THUẬT       ")
    print(f"        Chạy lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=========================================================\n")
    try:
        res = requests.get(WP_POSTS_API, auth=(WP_USERNAME, WP_APP_PASSWORD), params={"per_page": 10}, timeout=15)
        posts = res.json()
        
        total_score = 0
        report_log = []
        
        for post in posts:
            title = post['title']['rendered']
            content = post['content']['rendered']
            link = post['link']
            
            score, issues = evaluate_post(title, content)
            total_score += score
            
            status = "🟢 XUẤT SẮC" if score == 100 else ("🟡 CHẤP NHẬN ĐƯỢC" if score >= 80 else "🔴 KÉM")
            log_item = f"Bài: {title[:50]}...\n  -> Điểm: {score}/100 [{status}]\n"
            for issue in issues:
                log_item += f"    - LỖI: {issue}\n"
            
            print(log_item)
            report_log.append(log_item)
            
        avg_score = total_score / len(posts) if posts else 0
        final_verdict = f"\n[=] TÌNH TRẠNG BẢO MẬT SEO TỔNG THỂ: {avg_score}/100 ĐIỂM."
        print(final_verdict)
        
        # Lưu file nhật ký
        with open("seo_audit_report.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(report_log) + final_verdict)
            
    except Exception as e:
        print(f"[-] Hệ thống gặp lỗi khi quét: {e}")

if __name__ == "__main__":
    run_auditor()
