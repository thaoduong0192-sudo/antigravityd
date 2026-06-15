import requests
import json
import time

WP_API_URL = 'https://ecopets.vn/wp-json/wp/v2/posts'
AUTH = ('aivietbai', 'kNZG 0aEW 1iy0 tTcT Degh pTR4')

print('Bat dau xoa cac bai viet rac (category 503)...')
while True:
    res = requests.get(WP_API_URL, params={'categories': 503, 'per_page': 100}, auth=AUTH)
    if res.status_code != 200: 
        break
    posts = res.json()
    if not posts: 
        break
    for post in posts:
        del_res = requests.delete(f"{WP_API_URL}/{post['id']}", params={'force': True}, auth=AUTH)
        if del_res.status_code == 200: 
            print(f"Da xoa bai: {post['title']['rendered']}")
        else: 
            print(f"Loi xoa bai {post['id']}")
    time.sleep(1)

print('Da xoa sach bai cu.')

# Reset db
db_path = 'D:\\Antigravity\\ecopets_seo\\b2b_campaign_db.json'
with open(db_path, 'r', encoding='utf-8') as f: 
    db = json.load(f)

for kw in db.get('keywords', []): 
    kw['published_count'] = 0

with open(db_path, 'w', encoding='utf-8') as f: 
    json.dump(db, f, ensure_ascii=False, indent=4)

print('Da reset database.')
