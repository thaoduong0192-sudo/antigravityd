import requests, os
from dotenv import load_dotenv

load_dotenv()
WP_USERNAME = os.getenv('WP_USERNAME')
WP_APP_PASSWORD = os.getenv('WP_APP_PASSWORD')
WP_API_URL = 'https://giaiphapqrcode.com/wp-json/wp/v2/posts'
WP_MEDIA_URL = 'https://giaiphapqrcode.com/wp-json/wp/v2/media'

resp = requests.get(WP_API_URL + '?per_page=5', auth=(WP_USERNAME, WP_APP_PASSWORD))
posts = resp.json()

for p in posts:
    print(f"Post: {p['title']['rendered']}")
    print(f"  Featured Media ID: {p.get('featured_media')}")
    if p.get('featured_media'):
        media_resp = requests.get(f"{WP_MEDIA_URL}/{p['featured_media']}", auth=(WP_USERNAME, WP_APP_PASSWORD))
        if media_resp.status_code == 200:
            print(f"  Featured Media URL: {media_resp.json().get('source_url')}")
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(p['content']['rendered'], 'html.parser')
    imgs = soup.find_all('img')
    for img in imgs:
        print(f"  Body Image: {img.get('src')}")
    print('-'*40)
