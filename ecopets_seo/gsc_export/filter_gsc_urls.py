import csv
import os

CSV_FILE = "Bảng.csv"
OUTPUT_DIR = "."

def categorize_url(url):
    url = url.strip()
    if not url.startswith("http"):
        return "Unknown"
        
    # Check for old blogger URLs
    if url.endswith(".html") or "/feeds/" in url or "/search/" in url:
        return "System_Trash"
        
    # Check for common WP technical paths
    technical_paths = [
        "/tag/", "/category/", "/author/", "/feed", "/page/", 
        "/?p=", "/?wc-ajax=", "wp-includes", "wp-content", 
        "?add-to-cart=", "checkout", "elementor", "sitemap"
    ]
    
    for path in technical_paths:
        if path in url:
            return "System_Trash"
            
    # Check for products
    if "/products/" in url or "/product-tag/" in url or "/product-category/" in url:
        return "Products"
        
    # If none of the above, it's likely a blog post, a page, or the homepage
    return "Blog_Posts"

def main():
    print("Đang phân tích danh sách URL từ GSC...")
    
    categories = {
        "System_Trash": [],
        "Products": [],
        "Blog_Posts": [],
        "Unknown": []
    }
    
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            for row in reader:
                if not row:
                    continue
                url = row[0]
                cat = categorize_url(url)
                categories[cat].append(row)
                
    except FileNotFoundError:
        print(f"Không tìm thấy file {CSV_FILE}")
        return
        
    # Export results
    for cat_name, rows in categories.items():
        if rows:
            out_file = os.path.join(OUTPUT_DIR, f"{cat_name}.csv")
            with open(out_file, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header if header else ["URL", "Lần thu thập dữ liệu cuối cùng"])
                writer.writerows(rows)
            print(f"Đã lưu {len(rows)} URLs vào file {cat_name}.csv")
            
    print("Hoàn tất!")

if __name__ == "__main__":
    main()
