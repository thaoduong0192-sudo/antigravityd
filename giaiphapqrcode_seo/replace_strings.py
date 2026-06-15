import os
import glob

replacements = {
    "helloconsen.com": "giaiphapqrcode.com",
    "HelloConsen": "Giải Pháp QR Code",
    "HELLOCONSEN": "GIAIPHAPQRCODE",
    "helloconsen": "giaiphapqrcode",
    "Ecopets": "Giải Pháp QR Code",
    "Pet Shop Hữu Cơ": "Dịch vụ",
    "https://helloconsen.com/danh-muc/eco-pets": "https://giaiphapqrcode.com",
    "https://helloconsen.com": "https://giaiphapqrcode.com"
}

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

if __name__ == "__main__":
    base_dir = r"D:\Antigravity\giaiphapqrcode_seo"
    extensions = ['*.py', '*.bat', '*.vbs']
    
    for ext in extensions:
        for filepath in glob.glob(os.path.join(base_dir, ext)):
            if "replace_strings.py" in filepath:
                continue
            replace_in_file(filepath)
            
    # Rename files
    for filename in os.listdir(base_dir):
        if "helloconsen" in filename.lower() and filename != "replace_strings.py":
            old_path = os.path.join(base_dir, filename)
            new_name = filename.replace("helloconsen", "giaiphapqrcode")
            new_path = os.path.join(base_dir, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed {filename} to {new_name}")
