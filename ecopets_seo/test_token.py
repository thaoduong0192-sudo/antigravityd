import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request

JSON_KEY_FILE = r'D:\Antigravity\ecopets_seo\indexing-api-project-498111-d7a24ef04936.json'
SCOPES = ['https://www.googleapis.com/auth/indexing']

try:
    credentials = service_account.Credentials.from_service_account_file(
        JSON_KEY_FILE, scopes=SCOPES)
    credentials.refresh(Request())
    print("TOKEN_SUCCESS")
except Exception as e:
    print("TOKEN_ERROR:", e)
