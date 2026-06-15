import requests
import random

def test_wiki(keyword):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&generator=search&gsrsearch={keyword}&pithumbsize=1200"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        pages = data.get('query', {}).get('pages', {})
        for k, v in pages.items():
            if 'thumbnail' in v:
                print(v['thumbnail']['source'])
    else:
        print("Failed", res.status_code)

test_wiki("barcode")
