import os
import json
import sqlite3
import shutil
import base64
import logging
from pathlib import Path
from typing import Dict, Optional

try:
    import win32crypt
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    win32crypt = None
    AESGCM = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CookieExtractor")

class ChromeCookieExtractor:
    """Tự động trích xuất Session Cookies của Google NotebookLM từ trình duyệt Chrome local (Bảo vệ file lock)"""

    @staticmethod
    def get_chrome_local_state() -> Optional[bytes]:
        local_state_path = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Local State"
        if not local_state_path.exists():
            return None
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:] # Cut DPAPI header
            if win32crypt:
                decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                return decrypted_key
        except Exception as e:
            logger.warning(f"Không thể giải mã Local State Key: {e}")
        return None

    @staticmethod
    def get_notebooklm_cookies() -> Dict[str, str]:
        """Lấy cookies cho domain .google.com / notebooklm.google.com an toàn không bị nghẽn file lock"""
        cookies_db = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Network" / "Cookies"
        if not cookies_db.exists():
            cookies_db = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cookies"
        
        if not cookies_db.exists():
            logger.warning("Không tìm thấy file Cookies của Chrome.")
            return {}

        # Copy db ra temp với try-except an toàn nếu Chrome đang mở
        temp_db = Path(__file__).parent / "temp_cookies.db"
        cookies = {}

        try:
            # Nếu Chrome đang mở khóa file, đọc qua file stream hoặc bỏ qua lỗi
            try:
                shutil.copy2(cookies_db, temp_db)
            except PermissionError:
                logger.warning("Chrome đang khóa file Cookies. Đang bỏ qua lock để tiếp tục...")
                return {}
            except Exception as copy_err:
                logger.warning(f"Không thể copy file cookies: {copy_err}")
                return {}

            if temp_db.exists():
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT host_key, name, value, encrypted_value FROM cookies WHERE host_key LIKE '%google%'")
                
                key = ChromeCookieExtractor.get_chrome_local_state()

                for host, name, value, encrypted_value in cursor.fetchall():
                    if name in ["__Secure-1PSID", "__Secure-3PSID", "SAPISID", "HSID", "SSID", "APISID", "SID"]:
                        if value:
                            cookies[name] = value
                        elif encrypted_value and key and AESGCM:
                            try:
                                nonce = encrypted_value[3:15]
                                ciphertext = encrypted_value[15:]
                                aesgcm = AESGCM(key)
                                decrypted = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
                                cookies[name] = decrypted
                            except Exception:
                                pass
                conn.close()
        except Exception as e:
            logger.warning(f"Xử lý cookies hoàn tất: {e}")
        finally:
            if temp_db.exists():
                try:
                    os.remove(temp_db)
                except Exception:
                    pass

        return cookies

    @staticmethod
    def get_cookie_header_str() -> str:
        """Trả về chuỗi Cookie Header sẵn sàng dùng cho HTTP Requests"""
        try:
            # Kiểm tra biến môi trường trước
            env_cookie = os.getenv("NOTEBOOKLM_COOKIE", "")
            if env_cookie:
                return env_cookie

            cookie_dict = ChromeCookieExtractor.get_notebooklm_cookies()
            if cookie_dict:
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
                return cookie_str
        except Exception as e:
            logger.warning(f"Đọc cookie header: {e}")
        return ""
