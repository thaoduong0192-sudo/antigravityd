import sys, requests, os, base64
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
u = os.getenv('WP_USERNAME')
p = os.getenv('WP_APP_PASSWORD')
t = base64.b64encode(f"{u}:{p}".encode()).decode()

r = requests.get('https://helloconsen.com/wp-json/wp/v2/posts?status=draft,publish&per_page=100', headers={'Authorization': f'Basic {t}'})
data = r.json()

b2b_keywords = ["Nơi bán balo", "Trại nhân giống mèo", "Nơi triệt sản", "Tổng kho sỉ"]

count = 0
for p in data:
    title = p['title']['rendered']
    is_b2b = any(k in title for k in b2b_keywords)
    if len(p['categories']) == 0 and is_b2b:
        pid = p['id']
        dr = requests.delete(f'https://helloconsen.com/wp-json/wp/v2/posts/{pid}?force=true', headers={'Authorization': f'Basic {t}'})
        print(f"Deleted {pid} ({title}): {dr.status_code}")
        count += 1

print(f"Total deleted: {count}")
