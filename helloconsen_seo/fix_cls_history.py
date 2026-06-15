import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL", "https://helloconsen.com")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

WP_POSTS_API = f"{WP_URL}/wp-json/wp/v2/posts"

def fix_cls_issues():
    print("=========================================================================")
    print("    CHIẾN DỊCH VÁ LỖI CUMULATIVE LAYOUT SHIFT (CLS) BÀI VIẾT CŨ          ")
    print("=========================================================================")
    try:
        res = requests.get(WP_POSTS_API, auth=(WP_USERNAME, WP_APP_PASSWORD), params={"per_page": 50}, timeout=15)
        posts = res.json()
        
        fixed_count = 0
        for post in posts:
            post_id = post['id']
            title = post['title']['rendered']
            content = post['content']['rendered']
            
            needs_update = False
            new_content = content
            
            # Cấy Width=800, Height=500 và Lazy load vào TẤT CẢ các thẻ <img> thiếu thuộc tính này
            img_tags = re.findall(r'<img[^>]+>', new_content)
            for img in img_tags:
                if ' width="' not in img and ' height="' not in img:
                    # Tạo img mới cứng
                    modified_img = img.replace('/>', ' width="800" height="500" loading="lazy" />')
                    if modified_img == img:
                         modified_img = img.replace('>', ' width="800" height="500" loading="lazy" >')
                    
                    new_content = new_content.replace(img, modified_img)
                    needs_update = True
                    print(f"  -> Đã bắt được thẻ ảnh vô kỷ luật (Không kích thước) trong bài: {title[:30]}...")

            if needs_update:
                update_payload = {"content": new_content}
                ru = requests.post(f"{WP_POSTS_API}/{post_id}", auth=(WP_USERNAME, WP_APP_PASSWORD), json=update_payload, timeout=20)
                if ru.status_code == 200:
                    print("  [+] Sửa thành công Mã nguồn bài viết (✅ Đẩy lùi CLS).")
                    fixed_count += 1
                else:
                    print(f"  [-] Lỗi: {ru.text[:100]}")
                    
        print(f"\n✅ Đã tiêm vắc-xin CLS thành công cho {fixed_count}/50 bài mới nhất!")
    except Exception as e:
        print(f"[-] Hệ thống gặp lỗi: {e}")

if __name__ == "__main__":
    fix_cls_issues()
