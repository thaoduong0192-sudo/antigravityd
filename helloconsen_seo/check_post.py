import sys, requests, os, base64
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
u = os.getenv('WP_USERNAME')
p = os.getenv('WP_APP_PASSWORD')
t = base64.b64encode(f"{u}:{p}".encode()).decode()

r = requests.get('https://helloconsen.com/wp-json/wp/v2/posts/15284', headers={'Authorization': f'Basic {t}'})
print("TITLE:", r.json()['title']['rendered'])
print("CONTENT LENGTH:", len(r.json()['content']['rendered']))
print("CONTENT START:", r.json()['content']['rendered'][:200])
