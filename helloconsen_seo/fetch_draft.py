import os, requests, base64
from dotenv import load_dotenv
load_dotenv('d:/Antigravity/helloconsen_seo/.env')
u = os.getenv('WP_USERNAME')
p = os.getenv('WP_APP_PASSWORD')
t = base64.b64encode(f'{u}:{p}'.encode()).decode()
r = requests.get('https://helloconsen.com/wp-json/wp/v2/posts/14691', headers={'Authorization': f'Basic {t}'})
with open('draft_post.html', 'w', encoding='utf-8') as f:
    f.write(r.json().get('content', {}).get('rendered', 'Error fetching'))
