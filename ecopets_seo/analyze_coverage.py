import pandas as pd
import re

df = pd.read_csv(r'C:\Users\US\Downloads\ecopets_coverage_2026_06_01\Bảng.csv', encoding='utf-8')

urls = df['URL'].tolist()

feed_count = 0
tag_count = 0
category_count = 0
pagination_count = 0
product_count = 0
post_count = 0
other_count = 0

for url in urls:
    if '/feed' in url:
        feed_count += 1
    elif '/tag/' in url or '/product-tag/' in url:
        tag_count += 1
    elif '/category/' in url or '/product-category/' in url:
        category_count += 1
    elif '/page/' in url:
        pagination_count += 1
    elif '/products/' in url:
        product_count += 1
    elif re.match(r'^https?://ecopets\.vn/[a-z0-9-]+/?$', url): # typical post/page structure
        post_count += 1
    else:
        other_count += 1

print(f"Total URLs: {len(urls)}")
print(f"Feed URLs (/feed): {feed_count}")
print(f"Tag URLs (/tag/, /product-tag/): {tag_count}")
print(f"Category URLs (/category/): {category_count}")
print(f"Pagination URLs (/page/): {pagination_count}")
print(f"Product URLs (/products/): {product_count}")
print(f"Post/Page URLs: {post_count}")
print(f"Other URLs: {other_count}")
