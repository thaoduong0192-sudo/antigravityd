import os
import requests
import json
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [ "https://www.googleapis.com/auth/indexing" ]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
KEY_FILE = "google_service_account.json"

def notify_google_index(url, type="URL_UPDATED"):
    if not os.path.exists(KEY_FILE):
        print(f"[-] Bỏ qua Indexing API: Chưa tìm thấy tệp {KEY_FILE}")
        return False
        
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, scopes=SCOPES)
        http = creds.authorize(requests.Session())
        
        content = {
            "url": url,
            "type": type
        }
        
        response, content = http.request(ENDPOINT, method="POST", body=json.dumps(content))
        data = json.loads(content)
        
        if response.status == 200:
            print(f"[+] LẬP CHỈ MỤC THÀNH CÔNG (Real-time): Đã đẩy tín hiệu ép Google quét URL: {url}")
            return True
        else:
            print(f"[-] Google Indexing API từ chối. Lỗi: {data.get('error', {}).get('message')}")
            return False
    except Exception as e:
        print(f"[-] Lỗi Hệ thống Indexing API: {e}")
        return False

if __name__ == "__main__":
    test_url = "https://helloconsen.com/"
    notify_google_index(test_url)
