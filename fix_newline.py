import glob

for f in glob.glob('D:/Antigravity/*_seo/fully_auto_*.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix the literal newline inside the f-string that causes SyntaxError
    content = content.replace('print(f"\\n[+]', 'print(f"\\\\n[+]')
    content = content.replace('print(f"\\n[+] Đang chạy tiến trình', 'print(f"\\\\n[+] Đang chạy tiến trình')
    
    # To be absolutely sure, let's just replace the exact broken string pattern
    # It currently looks like:
    # print(f"
    # [+] Đang chạy...
    
    fixed_content = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == 'print(f"':
            # look ahead
            if i+1 < len(lines) and '[+]' in lines[i+1]:
                # Combine them into one line
                continue
        elif '[+] Đang chạy tiến trình đăng bài lúc:' in line and i > 0 and lines[i-1].strip() == 'print(f"':
            fixed_content[-1] = fixed_content[-1] + '\\n' + line.strip()
            continue
            
        fixed_content.append(line)
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write('\n'.join(fixed_content))

print("Fixed syntax error")
