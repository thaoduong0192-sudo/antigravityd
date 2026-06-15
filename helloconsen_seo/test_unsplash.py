from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://unsplash.com/s/photos/dog-eating', timeout=60000)
    page.wait_for_selector('img')
    html = page.content()
    
    # Unsplash format is usually "/photos/some-slug-PHOTOID"
    links = re.findall(r'href="/photos/([^"]+)"', html)
    
    ids = []
    for link in set(links):
        parts = link.split('-')
        if len(parts) > 1 and len(parts[-1]) == 11:
            ids.append(parts[-1])
            
    print('Found IDs:', len(ids))
    print(ids[:10])
    browser.close()
