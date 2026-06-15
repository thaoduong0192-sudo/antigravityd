# -*- coding: utf-8 -*-
"""
rebuild_database.py - Rebuild database.json từ keyword_clusters.json
và đếm bài đã đăng từ WordPress để set published_count đúng.
"""
import sys, json, os, requests
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

WP_URL          = "https://giaiphapqrcode.com"
WP_USERNAME     = os.getenv("WP_USERNAME", "bluedata")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_POSTS_API    = f"{WP_URL}/wp-json/wp/v2/posts"

print("=== REBUILD DATABASE.JSON ===\n")

# Load keyword_clusters.json
with open("keyword_clusters.json", encoding="utf-8") as f:
    clusters = json.load(f)

print(f"keyword_clusters.json: {len(clusters)} tu khoa")

# Load database.json cu (giu articles history)
old_db = {}
if os.path.exists("database.json"):
    with open("database.json", encoding="utf-8") as f:
        old_db = json.load(f)

old_articles = old_db.get("articles", [])
print(f"database.json cu: {len(old_articles)} articles")

# Dem bai da dang tren WordPress (lay toan bo)
print("\nDang dem bai tren WordPress...")
wp_posts = []
page = 1
while True:
    r = requests.get(WP_POSTS_API,
                     auth=(WP_USERNAME, WP_APP_PASSWORD),
                     params={"per_page": 100, "page": page, "status": "publish"},
                     timeout=30)
    if r.status_code != 200:
        break
    posts = r.json()
    if not posts:
        break
    wp_posts.extend(posts)
    total_pages = int(r.headers.get("X-WP-TotalPages", 1))
    print(f"  Trang {page}/{total_pages}: {len(wp_posts)} bai")
    if page >= total_pages:
        break
    page += 1

print(f"Tong bai tren WP: {len(wp_posts)}")

# Dem bai moi kw
from collections import defaultdict
kw_count = defaultdict(int)
for post in wp_posts:
    title = post["title"]["rendered"].lower()
    for kw in clusters.keys():
        kw_lower = kw.lower()
        # Kiem tra xem title co chua keyword khong
        kw_words = kw_lower.split()[:3]  # 3 tu dau
        if all(w in title for w in kw_words):
            kw_count[kw] += 1
            break

# Xay dung keywords list moi
keywords_new = []
for kw, insights in clusters.items():
    published = kw_count.get(kw, 0)
    longtails = [i for i in insights if isinstance(i, str) and len(i) > 10][:9]
    keywords_new.append({
        "keyword": kw,
        "published_count": published,
        "longtails": longtails,
        "pillar_url": ""
    })
    if published > 0:
        print(f"  [{published:2d} bai] {kw[:55]}")

# Sap xep: kw chua du 10 bai len truoc
keywords_new.sort(key=lambda x: x["published_count"])

# Ghi database.json moi
new_db = {
    "keywords": keywords_new,
    "articles": old_articles
}

with open("database.json", "w", encoding="utf-8") as f:
    json.dump(new_db, f, ensure_ascii=False, indent=2)

available = [k for k in keywords_new if k["published_count"] < 10]
print(f"\n=== KET QUA ===")
print(f"Tong keywords: {len(keywords_new)}")
print(f"Can viet them (< 10 bai): {len(available)}")
if available:
    k = available[0]
    print(f"Keyword tiep theo: {k['keyword'][:60]} ({k['published_count']}/10)")
print("\ndatabase.json da duoc rebuild thanh cong!")
