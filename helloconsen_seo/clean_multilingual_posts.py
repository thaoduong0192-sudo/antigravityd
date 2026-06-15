import sys, requests, os, base64, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
u = os.getenv('WP_USERNAME')
p = os.getenv('WP_APP_PASSWORD')
t = base64.b64encode(f"{u}:{p}".encode()).decode()

state_path = "b2b_campaign_state.json"
with open(state_path, 'r', encoding='utf-8') as f:
    state = json.load(f)

print("Fetching latest posts...")
r = requests.get('https://helloconsen.com/wp-json/wp/v2/posts?status=publish&per_page=100', headers={'Authorization': f'Basic {t}'})
data = r.json()

count = 0
for p_data in data:
    pid = p_data['id']
    title = p_data['title']['rendered']
    
    # All posts from today's run
    if pid >= 15303:
        dr = requests.delete(f'https://helloconsen.com/wp-json/wp/v2/posts/{pid}?force=true', headers={'Authorization': f'Basic {t}'})
        print(f"Deleted {pid} ({title}): {dr.status_code}")
        count += 1
        
        # Extract base keyword from title
        # The title format is "{keyword} - {angle}" or something similar
        # Since we modified the prompt to output "Title: [Tiêu đề Clickbait hấp dẫn]" we can't easily guess the EXACT base keyword from the title anymore.
        # But wait! We know the exact keywords processed today. They were:
        # "Dịch vụ gỡ rối lông, trị rụng lông mèo tại", "Đại lý phân phối thức ăn chó mèo giá sỉ", "Cấp cứu chó mèo ban đêm ở"
        pass

# Hardcode decrementing the exact 3 keywords processed today so we don't guess wrong
keywords_to_reset = [
    "Dịch vụ gỡ rối lông, trị rụng lông mèo tại",
    "Đại lý phân phối thức ăn chó mèo giá sỉ",
    "Cấp cứu chó mèo ban đêm ở"
]

for kw in keywords_to_reset:
    # Need to find the correct mojibake key in the state file that corresponds to these words, OR just reset all articles_posted to 0 since we only have ~6 keywords fully processed!
    pass

# Wait, instead of manually matching mojibake, I will just reset the last 3 processed keywords in the state file
with open(state_path, 'w', encoding='utf-8') as f:
    # We will decrement the 'total_articles_posted' by count
    state["total_articles_posted"] = max(0, state["total_articles_posted"] - count)
    
    # Find keywords that have articles_posted > 0 and decrement them
    # Since only 6 keywords have 10 articles posted, let's just reset the ones that look like they were done today.
    # Actually, we can just reset any keyword that has articles_posted > 0, wait NO, we don't want to lose the good ones.
    # The good ones were generated on May 17th:
    # "Spa cắt móng...", "Siêu thị thú cưng lớn nhất...", "Học nghề cắt tỉa lông...", "Nơi gửi chó mèo dịp lễ Tết...", "Dịch vụ tắm sấy chó mèo lấy liền..."
    # The ones from today: "Dịch vụ gỡ rối...", "Đại lý phân phối...", "Cấp cứu chó mèo ban đêm..."
    
    # We can identify today's keywords by the ones we saw in the logs
    for key in list(state['keywords_status'].keys()):
        if "g r`i lA'ng" in key or "D<ch v" in key:  # Dịch vụ gỡ rối
            if state['keywords_status'][key]['articles_posted'] > 0:
                state['keywords_status'][key]['articles_posted'] = 0
                print("Reset count for:", key)
        if "?i lA phAn ph`i" in key or "giA s%" in key: # Đại lý phân phối
            if state['keywords_status'][key]['articles_posted'] > 0:
                state['keywords_status'][key]['articles_posted'] = 0
                print("Reset count for:", key)
        if "Cp ccu" in key: # Cấp cứu chó mèo ban đêm
            if state['keywords_status'][key]['articles_posted'] > 0:
                state['keywords_status'][key]['articles_posted'] = 0
                print("Reset count for:", key)
                
    json.dump(state, f, ensure_ascii=False, indent=4)

print(f"Total deleted: {count}")
