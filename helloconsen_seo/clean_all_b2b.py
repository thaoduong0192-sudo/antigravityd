import sys, requests, os, base64
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
u = os.getenv('WP_USERNAME')
p = os.getenv('WP_APP_PASSWORD')
t = base64.b64encode(f"{u}:{p}".encode()).decode()

r = requests.get('https://helloconsen.com/wp-json/wp/v2/posts?status=draft,publish&per_page=100', headers={'Authorization': f'Basic {t}'})
data = r.json()

count = 0
for p in data:
    pid = p['id']
    if pid > 14700 and len(p['categories']) == 0:
        dr = requests.delete(f'https://helloconsen.com/wp-json/wp/v2/posts/{pid}?force=true', headers={'Authorization': f'Basic {t}'})
        print(f"Deleted {pid} ({p['title']['rendered']}): {dr.status_code}")
        count += 1

print(f"Total deleted: {count}")

if os.path.exists('b2b_campaign_state.json'):
    os.remove('b2b_campaign_state.json')
    print("Reset b2b_campaign_state.json")
