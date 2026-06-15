import os
import requests
import random
from dotenv import load_dotenv

load_dotenv()

WC_KEY = os.getenv("WC_CONSUMER_KEY")
WC_SECRET = os.getenv("WC_CONSUMER_SECRET")
WC_URL = "https://ecopets.vn/wp-json/wc/v3"

reviews = [
    {"reviewer": "Minh Tuấn", "reviewer_email": "tuanminh9x@gmail.com", "review": "Sản phẩm xài rất tốt, bé nhà mình hợp tác ngay từ lần đầu. Đóng gói cẩn thận, giao hàng nhanh. Sẽ ủng hộ shop dài dài!"},
    {"reviewer": "Hải Yến", "reviewer_email": "haiyen.ng@hotmail.com", "review": "Bé nhà mình kén ăn mà từ lúc dùng sản phẩm này trộm vía ăn ngoan hơn hẳn. Chất lượng tuyệt vời, vote 5 sao cho shop!"},
    {"reviewer": "Phương Thảo", "reviewer_email": "thaophuong1995@yahoo.com", "review": "Đã mua lần thứ 2, chất lượng vẫn ổn định như ngày nào. Mùi thơm dễ chịu, boss rất thích. Cảm ơn shop tư vấn nhiệt tình."},
    {"reviewer": "Tuấn Khang", "reviewer_email": "tuankhang.tran@gmail.com", "review": "Giá cả hợp lý so với chất lượng. Mọi người nên mua thử cho bé ở nhà dùng nha, hiệu quả thấy rõ sau 1 tuần luôn."},
    {"reviewer": "Ngọc Ánh", "reviewer_email": "ngocanh_kitty@gmail.com", "review": "Hàng chính hãng, date xa. Dùng rất yên tâm, lông bé mềm mượt và bớt rụng hẳn. Sẽ giới thiệu cho bạn bè."}
]

def get_all_products():
    products = []
    page = 1
    while True:
        resp = requests.get(
            f"{WC_URL}/products",
            auth=(WC_KEY, WC_SECRET),
            params={"status": "publish", "per_page": 50, "page": page}
        )
        if resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        products.extend(data)
        page += 1
    return products

def check_product_reviews(product_id):
    resp = requests.get(
        f"{WC_URL}/products/reviews",
        auth=(WC_KEY, WC_SECRET),
        params={"product": [product_id]}
    )
    if resp.status_code == 200:
        return len(resp.json())
    return 0

def add_review(product_id):
    num_reviews = check_product_reviews(product_id)
    if num_reviews > 0:
        print(f"Sản phẩm ID {product_id} đã có {num_reviews} đánh giá. Bỏ qua.")
        return

    rev_data = random.choice(reviews)
    payload = {
        "product_id": product_id,
        "review": rev_data["review"],
        "reviewer": rev_data["reviewer"],
        "reviewer_email": rev_data["reviewer_email"],
        "rating": 5,
        "verified": True
    }
    
    resp = requests.post(
        f"{WC_URL}/products/reviews",
        auth=(WC_KEY, WC_SECRET),
        json=payload
    )
    if resp.status_code == 201:
        print(f"[+] Đã thêm đánh giá 5 sao cho sản phẩm ID {product_id}!")
    else:
        print(f"[-] Lỗi thêm đánh giá cho SP {product_id}: {resp.text}")

if __name__ == "__main__":
    print("Đang lấy danh sách sản phẩm...")
    prods = get_all_products()
    print(f"Tìm thấy {len(prods)} sản phẩm. Tiến hành quét đánh giá...")
    for p in prods:
        add_review(p['id'])
    print("Hoàn tất chiến dịch seeding Review!")
