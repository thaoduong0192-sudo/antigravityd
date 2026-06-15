import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"

def publish_wp_drafts():
    print("Đang tìm bài viết nháp trên Ecopets...")
    try:
        response = requests.get(
            WP_API_URL,
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            params={"status": "draft", "per_page": 100},
            timeout=15
        )
        if response.status_code == 200:
            drafts = response.json()
            if not drafts:
                print("Không tìm thấy bài viết nháp nào trên site.")
                return

            print(f"Tìm thấy {len(drafts)} bài viết nháp. Đang publish...")
            for post in drafts:
                post_id = post['id']
                title = post.get('title', {}).get('rendered', 'Unknown')
                update_res = requests.post(
                    f"{WP_API_URL}/{post_id}",
                    auth=(WP_USERNAME, WP_APP_PASSWORD),
                    json={"status": "publish"},
                    timeout=10
                )
                if update_res.status_code == 200:
                    print(f" [+] Đã publish thành công: {title}")
                else:
                    print(f" [-] Lỗi khi publish post {post_id}: {update_res.text}")
        else:
            print(f"Lỗi truy xuất drafts WP: {response.text}")
    except Exception as e:
         print(f"Lỗi: {e}")

def update_database_json():
    db_path = "database.json"
    if not os.path.exists(db_path):
        print("Không tìm thấy database.json")
        return
        
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        updated = False
        for article in db.get("articles", []):
            if article.get("status") == "Draft":
                article["status"] = "Published"
                updated = True
                print(f" Cập nhật DB nội bộ cho bài: {article.get('title')}")
                
        if updated:
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            print("Đã lưu lại trạng thái mới vào database.json")
        else:
             print("Không có bài nào trạng thái Draft trong database.json")
             
    except Exception as e:
        print(f"Lỗi đọc/ghi database.json: {e}")

if __name__ == "__main__":
    if not WP_USERNAME or not WP_APP_PASSWORD:
         print("Thiếu credentials cấu hình WP. Hãy kiểm tra file .env hoặc sửa script.")
         exit(1)
         
    publish_wp_drafts()
    update_database_json()
    print("Hoàn tất quy trình publish nháp cũ!")
