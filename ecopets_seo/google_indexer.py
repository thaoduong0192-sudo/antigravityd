import os
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

JSON_KEY_FILE = r'D:\Antigravity\ecopets_seo\indexing-api-project-498111-d7a24ef04936.json'
SCOPES = ['https://www.googleapis.com/auth/indexing']
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

def request_indexing(url):
    """
    Sử dụng Google Indexing API để gửi yêu cầu index ngay lập tức.
    """
    try:
        if not os.path.exists(JSON_KEY_FILE):
            print(f"[INDEXING API] Không tìm thấy file JSON: {JSON_KEY_FILE}")
            return False
            
        credentials = service_account.Credentials.from_service_account_file(JSON_KEY_FILE, scopes=SCOPES)
        authed_session = AuthorizedSession(credentials)
        
        response = authed_session.post(
            ENDPOINT,
            json={
                "url": url,
                "type": "URL_UPDATED"
            }
        )
        
        if response.status_code == 200:
            print(f"[INDEXING API] Đã gửi yêu cầu Index thành công cho: {url}")
            return True
        else:
            print(f"[INDEXING API] Lỗi ({response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"[INDEXING API] Exception: {e}")
        return False

if __name__ == "__main__":
    # Test
    request_indexing("https://ecopets.vn/")
