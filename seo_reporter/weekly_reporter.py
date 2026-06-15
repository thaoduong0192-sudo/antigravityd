import os
import requests
import json
import datetime
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GSC_AVAILABLE = True
except ImportError:
    GSC_AVAILABLE = False

# Define sites and their env paths
SITES = [
    {
        "name": "HelloConsen",
        "url": "https://helloconsen.com",
        "env_path": r"D:\Antigravity\helloconsen_seo\.env",
        "gsc_url": "sc-domain:helloconsen.com" # Or https://helloconsen.com/
    },
    {
        "name": "Ecopets",
        "url": "https://ecopets.vn",
        "env_path": r"D:\Antigravity\ecopets_seo\.env",
        "gsc_url": "sc-domain:ecopets.vn"
    },
    {
        "name": "Hồi Ký",
        "url": "https://hoiky.com.vn",
        "env_path": r"D:\Antigravity\hoiky_seo\.env",
        "gsc_url": "sc-domain:hoiky.com.vn"
    },
    {
        "name": "Giải Pháp QRCode",
        "url": "https://giaiphapqrcode.com",
        "env_path": r"D:\Antigravity\giaiphapqrcode_seo\.env",
        "gsc_url": "sc-domain:giaiphapqrcode.com"
    }
]

REPORT_DIR = r"D:\Antigravity\báo cáo"
GSC_KEY_PATH = r"D:\Antigravity\seo_reporter\gsc_credentials.json"

def load_wp_credentials(env_path):
    load_dotenv(env_path)
    return os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD")

def fetch_recent_posts(site_url, username, password, days=7):
    date_threshold = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
    api_url = f"{site_url}/wp-json/wp/v2/posts"
    params = {
        "after": date_threshold,
        "per_page": 100,
        "status": "publish"
    }
    
    auth = (username, password) if username and password else None
    
    try:
        response = requests.get(api_url, params=params, auth=auth, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching from {site_url}: {e}")
        return []

def get_gsc_service():
    if not GSC_AVAILABLE or not os.path.exists(GSC_KEY_PATH):
        return None
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GSC_KEY_PATH, scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
        service = build('webmasters', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Lỗi kết nối GSC: {e}")
        return None

def fetch_gsc_data(service, site_url, days=7):
    if not service:
        return {"clicks": "N/A", "impressions": "N/A", "top_keywords": []}
    
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    
    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query'],
        'rowLimit': 5
    }
    
    try:
        # Check if site is domain property or url prefix
        # Usually it's sc-domain:example.com or https://example.com/
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        rows = response.get('rows', [])
        
        total_clicks = sum([row['clicks'] for row in rows]) if rows else 0
        total_impressions = sum([row['impressions'] for row in rows]) if rows else 0
        
        top_keywords = [row['keys'][0] for row in rows[:5]]
        
        return {
            "clicks": int(total_clicks),
            "impressions": int(total_impressions),
            "top_keywords": top_keywords
        }
    except Exception as e:
        print(f"Lỗi lấy dữ liệu GSC cho {site_url}: {e}")
        return {"clicks": "N/A", "impressions": "N/A", "top_keywords": []}

def generate_html_report(data, date_str):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Báo Cáo SEO Tổng Quan - {date_str}</title>
        <style>
            :root {{
                --bg-main: #0f172a;
                --bg-card: #1e293b;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --accent-1: #3b82f6;
                --accent-2: #10b981;
                --border-color: #334155;
            }}
            body {{
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                background-color: var(--bg-main);
                color: var(--text-main);
                margin: 0;
                padding: 40px 20px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 50px;
            }}
            .header h1 {{
                font-size: 2.5rem;
                background: linear-gradient(135deg, #60a5fa, #34d399);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 30px;
            }}
            .card {{
                background-color: var(--bg-card);
                border-radius: 16px;
                padding: 30px;
                border: 1px solid var(--border-color);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
            }}
            .card:hover {{
                transform: translateY(-5px);
            }}
            .card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid var(--border-color);
            }}
            .site-name {{
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--accent-1);
            }}
            .stats-pill {{
                background-color: rgba(59, 130, 246, 0.1);
                color: #60a5fa;
                padding: 6px 12px;
                border-radius: 999px;
                font-size: 0.875rem;
                font-weight: 600;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-bottom: 25px;
            }}
            .metric-box {{
                background-color: rgba(15, 23, 42, 0.5);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--accent-2);
            }}
            .metric-label {{
                font-size: 0.8rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-top: 5px;
            }}
            .keyword-list {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 20px;
            }}
            .keyword-tag {{
                background: rgba(16, 185, 129, 0.1);
                color: #10b981;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 0.85rem;
            }}
            .post-list {{
                list-style: none;
                padding: 0;
                margin: 0;
                max-height: 250px;
                overflow-y: auto;
            }}
            .post-list::-webkit-scrollbar {{
                width: 6px;
            }}
            .post-list::-webkit-scrollbar-thumb {{
                background-color: var(--border-color);
                border-radius: 3px;
            }}
            .post-item {{
                margin-bottom: 12px;
                padding-bottom: 12px;
                border-bottom: 1px dashed var(--border-color);
            }}
            .post-item:last-child {{
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }}
            .post-item a {{
                color: var(--text-main);
                text-decoration: none;
                font-size: 0.95rem;
                transition: color 0.2s ease;
            }}
            .post-item a:hover {{
                color: var(--accent-1);
            }}
            .no-posts {{
                color: var(--text-muted);
                font-style: italic;
                text-align: center;
                padding: 20px 0;
            }}
            .note {{
                margin-top: 50px;
                text-align: center;
                color: var(--text-muted);
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Báo Cáo SEO & Content Hàng Tuần</h1>
                <p>Tổng hợp dữ liệu 7 ngày qua - Cập nhật ngày {date_str}</p>
            </div>
            <div class="grid">
    """
    
    for site in data:
        html_content += f"""
                <div class="card">
                    <div class="card-header">
                        <div class="site-name">{site['name']}</div>
                        <div class="stats-pill">{len(site['posts'])} Bài Viết Mới</div>
                    </div>
                    
                    <div class="metrics">
                        <div class="metric-box">
                            <div class="metric-value">{site['gsc']['clicks']}</div>
                            <div class="metric-label">Click (7 ngày)</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-value">{site['gsc']['impressions']}</div>
                            <div class="metric-label">Hiển thị (7 ngày)</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-value">{len(site['gsc']['top_keywords'])}</div>
                            <div class="metric-label">Từ khóa lọt Top</div>
                        </div>
                    </div>
        """
        
        if site['gsc']['top_keywords']:
            html_content += """<div class="keyword-list">"""
            for kw in site['gsc']['top_keywords']:
                html_content += f"""<span class="keyword-tag">{kw}</span>"""
            html_content += """</div>"""
            
        html_content += """
                    <h4>Bài viết mới nhất:</h4>
                    <ul class="post-list">
        """
        if site['posts']:
            for post in site['posts']:
                title = post.get('title', {}).get('rendered', 'No Title')
                link = post.get('link', '#')
                html_content += f"""
                        <li class="post-item">
                            <a href="{link}" target="_blank">{title}</a>
                        </li>
                """
        else:
            html_content += """
                        <li class="no-posts">Không có bài viết nào được xuất bản.</li>
            """
            
        html_content += """
                    </ul>
                </div>
        """
        
    html_content += f"""
            </div>
            <div class="note">
                {'* Đã tích hợp Google Search Console thành công.' if GSC_AVAILABLE and os.path.exists(GSC_KEY_PATH) else '* Lưu ý: Dữ liệu Click/Hiển thị đang trống do chưa kết nối GSC. Hãy xem hướng dẫn kết nối để cấu hình.'}
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def show_popup(report_path):
    root = tk.Tk()
    root.withdraw() # Hide the main window
    root.attributes("-topmost", True) # Ensure it's on top
    messagebox.showinfo(
        "Báo Cáo SEO Hàng Tuần Đã Sẵn Sàng", 
        f"Đã tạo thành công báo cáo SEO cho 4 website.\n\nFile được lưu tại:\n{report_path}\n\nHãy mở file HTML trên trình duyệt để xem báo cáo tổng quan."
    )
    root.destroy()

def main():
    print("Bắt đầu thu thập dữ liệu...")
    
    gsc_service = get_gsc_service()
    if gsc_service:
        print("[+] Đã kết nối thành công với Google Search Console API.")
    else:
        print("[-] Chưa cấu hình Google Search Console. Bỏ qua lấy dữ liệu từ khóa.")

    report_data = []
    
    for site in SITES:
        print(f"Đang xử lý: {site['name']}...")
        username, password = load_wp_credentials(site['env_path'])
        
        posts = fetch_recent_posts(site['url'], username, password)
        gsc_data = fetch_gsc_data(gsc_service, site['gsc_url'])
        
        report_data.append({
            "name": site['name'],
            "posts": posts,
            "gsc": gsc_data
        })
        
    print("Đang tạo file báo cáo HTML...")
    date_str = datetime.datetime.now().strftime("%d-%m-%Y")
    html_report = generate_html_report(report_data, date_str)
    
    file_name = f"Bao_Cao_SEO_{date_str}.html"
    file_path = os.path.join(REPORT_DIR, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_report)
        
    print(f"Hoàn thành! Báo cáo đã được lưu tại: {file_path}")
    show_popup(file_path)

if __name__ == "__main__":
    main()
