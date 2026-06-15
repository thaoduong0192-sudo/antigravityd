import sys, requests, os, base64, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
u = os.getenv('WP_USERNAME')
p = os.getenv('WP_APP_PASSWORD')
t = base64.b64encode(f"{u}:{p}".encode()).decode()

state_path = "b2b_campaign_state.json"
with open(state_path, 'r', encoding='utf-8') as f:
    state = json.load(f)

print("Fetching latest posts...")
r = requests.get('https://helloconsen.com/wp-json/wp/v2/posts?status=draft,publish&per_page=100', headers={'Authorization': f'Basic {t}'})
data = r.json()

count = 0
for p_data in data:
    content_len = len(p_data['content']['rendered'])
    title = p_data['title']['rendered']
    
    # Empty or very short content
    if content_len < 500:
        pid = p_data['id']
        dr = requests.delete(f'https://helloconsen.com/wp-json/wp/v2/posts/{pid}?force=true', headers={'Authorization': f'Basic {t}'})
        print(f"Deleted {pid} ({title}) - Len: {content_len}: {dr.status_code}")
        count += 1
        
        # Decrement state
        if title in state["keywords_status"]:
            state["keywords_status"][title]["articles_posted"] = max(0, state["keywords_status"][title]["articles_posted"] - 1)
            print(f"Decremented count for '{title}'")

with open(state_path, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=4)

print(f"Total deleted: {count}")
