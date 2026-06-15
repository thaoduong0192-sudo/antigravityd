import sys, requests, os, base64
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
u = os.getenv('WP_USERNAME')
p = os.getenv('WP_APP_PASSWORD')
t = base64.b64encode(f"{u}:{p}".encode()).decode()

bad_ids = [14691, 14689, 14686, 14682, 14678, 14676, 14674, 14672]
for pid in bad_ids:
    r = requests.delete(f'https://helloconsen.com/wp-json/wp/v2/posts/{pid}?force=true', headers={'Authorization': f'Basic {t}'})
    print(f"Deleted {pid}: {r.status_code}")

if os.path.exists('b2b_campaign_state.json'):
    os.remove('b2b_campaign_state.json')
    print("Reset b2b_campaign_state.json")
