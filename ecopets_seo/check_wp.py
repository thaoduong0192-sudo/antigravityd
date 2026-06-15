import requests
posts = requests.get('https://ecopets.vn/wp-json/wp/v2/posts?per_page=15').json()
for p in posts:
    print(f"ID: {p['id']} - Title: {p['title']['rendered']}")
