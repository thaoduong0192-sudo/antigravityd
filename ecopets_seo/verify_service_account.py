import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

JSON_KEY_FILE = r'D:\Antigravity\ecopets_seo\indexing-api-project-498111-d7a24ef04936.json'
SCOPES = ['https://www.googleapis.com/auth/siteverification']

def verify_site():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            JSON_KEY_FILE, scopes=SCOPES)
        service = build('siteVerification', 'v1', credentials=credentials)

        print("Verifying ownership for https://ecopets.vn/ ...")
        request_body = {
            "site": {
                "identifier": "https://ecopets.vn/",
                "type": "SITE"
            }
        }
        
        response = service.webResource().insert(verificationMethod="META", body=request_body).execute()
        print("Response:", response)
        print("SUCCESSS! Service account is now an owner.")
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    verify_site()
