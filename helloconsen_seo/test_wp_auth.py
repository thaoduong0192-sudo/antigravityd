import os
import requests
from dotenv import load_dotenv

load_dotenv()

WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_API_URL = "https://helloconsen.com/wp-json/wp/v2/posts"

print(f"User: {WP_USERNAME}")
print(f"Pass: {WP_APP_PASSWORD}")

response = requests.get(WP_API_URL + "?per_page=1", auth=(WP_USERNAME, WP_APP_PASSWORD))
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(response.text)
