import sys, requests, os, base64
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
u = os.getenv('WP_USERNAME')
p = os.getenv('WP_APP_PASSWORD')
t = base64.b64encode(f"{u}:{p}".encode()).decode()
r = requests.get('https://helloconsen.com/wp-json/wp/v2/posts?status=draft,publish&per_page=50', headers={'Authorization': f'Basic {t}'})
data = r.json()
print(f"Found {len(data)} posts")
for p in data:
    print(f"ID: {p['id']} - Status: {p['status']} - Categories: {p['categories']} - Title: {p['title']['rendered']}")
