import os
import requests
from bs4 import BeautifulSoup
from google_indexing import notify_google_index

SITEMAP_URL = "http://giaiphapqrcode.com/sitemap_index.xml"

def crawl_sitemaps(url):
    print(f"[*] Đang lấy dữ liệu XML từ: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        
        # Sitemaps con
        sub_sitemaps = soup.find_all('sitemap')
        if sub_sitemaps:
            print(f"  -> Phát hiện {len(sub_sitemaps)} bản đồ con. Đang bóc tách...")
            urls = []
            for sm in sub_sitemaps:
                loc = sm.find('loc').text
                # Chỉ lấy bài viếc / page, bỏ qua category nếu muốn
                if "post-sitemap" in loc or "page-sitemap" in loc or "product-sitemap" in loc:
                    urls.extend(crawl_sitemaps(loc))
            return urls
            
        # URL chính
        locations = soup.find_all('url')
        print(f"  -> Lấy được {len(locations)} URL.")
        return [loc.find('loc').text for loc in locations if loc.find('loc')]
        
    except Exception as e:
        print(f"[-] Lỗi phân tích sitemap {url}: {e}")
        return []

def main():
    print("=====================================================================")
    print("      GIAIPHAPQRCODE - CHIẾN DỊCH QUÉT BẢN ĐỒ VÀ BẮN INDEX HÀNG LOẠT    ")
    print("=====================================================================")
    print("⚠️  Lưu ý: Chỉ thực hiện khi có file google_service_account.json   \n")
    
    if not os.path.exists("google_service_account.json"):
        print("[-] DỪNG: Bạn chưa cấu hình Tài khoản Google Indexing API (Thiếu file json).")
        return
        
    all_urls = crawl_sitemaps(SITEMAP_URL)
    all_urls = list(set(all_urls)) # Xóa trùng lặp
    print(f"\n[+] Tổng cộng gom được: {len(all_urls)} URL sạch (Sản phẩm, Bài viết...)")
    
    print("\n[🚀] BẮT ĐẦU ÉP GOOGLE QUÉT HÀNG LOẠT...")
    success_count = 0
    for i, url in enumerate(all_urls):
        result = notify_google_index(url)
        if result: success_count += 1
        
    print("\n✅ HOÀN TẤT CHIẾN DỊCH ÉP XUNG!")
    print(f"  - Thành công đẩy lên Google: {success_count}/{len(all_urls)} URLs.")
    
if __name__ == "__main__":
    main()
