import os
import time

with open('tmp_gemini.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

index_end = 0
for i, line in enumerate(lines):
    if "if not image_url or not img_locator:" in line:
        index_end = i
        break

new_code = """            if not image_url or not img_locator:
                print("❌ Không tìm thấy ảnh từ Gemini. Đuổi về Pollinations dự phòng.")
                await context.close()
                return None
                
            os.makedirs("fb_images", exist_ok=True)
            save_path = os.path.abspath(os.path.join("fb_images", f"gemini_{int(time.time())}.jpg"))

            print("⏳ Đang tải ảnh NGUYÊN BẢN từ URL gốc (chất lượng cao nhất)...")
            try:
                import requests as req_lib
                cookies_list = await context.cookies()
                cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies_list])
                
                dl_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                    "Cookie": cookie_header,
                    "Referer": "https://gemini.google.com/",
                }
                resp = req_lib.get(image_url, headers=dl_headers, timeout=60)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    with open(save_path, 'wb') as f:
                        f.write(resp.content)
                    file_size = os.path.getsize(save_path)
                    print(f"✅ Đã tải ảnh NGUYÊN VẸN từ URL gốc ({file_size//1024} KB).")
                    
                    try:
                        import subprocess
                        print("💉 Đang dùng PowerShell ép ảnh vào Clipboard...")
                        abs_save_path = os.path.abspath(save_path).replace('\\\\', '\\\\\\\\')
                        ps_script = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{abs_save_path}'))"
                        subprocess.run(["powershell", "-c", ps_script], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        print("✅ Đã bơm ảnh thành công vào Clipboard! Sẵn sàng sang Facebook bấm Ctrl+V.")
                        
                        await context.close()
                        return "CLIPBOARD"
                    except Exception as ps_err:
                        print(f"⚠️ Lỗi ép Clipboard bằng PowerShell: {ps_err}")
                else:
                    print(f"⚠️ Tải URL gốc thất bại (status={resp.status_code}).")
            except Exception as dl_err:
                print(f"⚠️ Lỗi tải URL: {dl_err}.")
                
            print("❌ Tất cả chiến lược tải ảnh đều thất bại. Đuổi về Pollinations dự phòng.")
            await context.close()
            return None
            
        except Exception as flow_err:
            print(f"❌ Luồng Khai Xuất Ảnh Web Đứng Bánh: {flow_err}")
            await context.close()
            return None
"""

with open('gemini_image_generator.py', 'w', encoding='utf-8') as f:
    f.writelines(lines[:index_end])
    f.write(new_code)
