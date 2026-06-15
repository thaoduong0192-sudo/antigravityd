import os

env_path = "D:/Antigravity/ecopets_seo/.env"
try:
    with open(env_path, "rb") as f:
        data = f.read()
    
    # Dọn dẹp null bytes do powershell echo gây ra
    clean_data = data.replace(b'\x00', b'')
    clean_text = clean_data.decode('utf-8', errors='ignore')
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(clean_text)
    print("Đã dọn dẹp .env")
except Exception as e:
    print("Lỗi:", e)
