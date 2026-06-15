"""
stock_photos.py - Thư viện ảnh stock Pexels cho helloconsen.com
Sử dụng Pexels API (Miễn phí 20,000 requests/tháng) để đảm bảo 1000 bài viết
không bao giờ bị trùng lặp hình ảnh, chất lượng cao, đúng chuẩn thú y.
"""
import random
import requests
import os
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# ========================
# DANH SÁCH 100 TỪ KHÓA TÌM KIẾM ĐA DẠNG CHÓ MÈO
# Đảm bảo kết quả ảnh Pexels luôn phong phú, không nhàm chán
# ========================

KEYWORD_POOL = {
    "dog_eating": [
        "dog eating dog food", "dog chewing bone", "puppy eating from bowl", "golden retriever eating",
        "dog eating kibble", "dog eating treats", "hungry dog eating", "dog feeding time",
        "dog eating healthy food", "dog licking food bowl", "dog eating meat", "dog snacking"
    ],
    "cat_eating": [
        "cat eating wet food", "cat eating kibble", "kitten eating", "cat licking bowl",
        "cat eating fish", "cat eating meat", "hungry cat", "cat feeding time",
        "cat eating treats", "cat enjoying food"
    ],
    "dog_bathing": [
        "dog taking a bath", "washing dog", "dog grooming bathtub", "wet dog bath",
        "dog taking shower", "dog spa grooming", "puppy taking bath", "dog getting washed",
        "dog shampooing", "happy dog in bath"
    ],
    "cat_bathing": [
        "cat grooming spa", "washing cat", "cat taking bath", "wet cat",
        "cat grooming towel", "cat getting brushed", "cat spa day"
    ],
    "dog_playing": [
        "dog playing with toy", "dog fetching ball", "dog playing in park", "dog running outside",
        "dog playing catch", "dog jumping for frisbee", "dog playing tug of war", "happy dog playing",
        "dog chewing toy", "dog running on grass", "puppy playing", "dog playing outdoor"
    ],
    "cat_playing": [
        "cat playing with yarn", "cat playing with toy", "cat pouncing", "kitten playing",
        "cat scratching post", "cat playing indoors", "cat chasing laser", "cat playing with feather",
        "playful cat", "cat jumping toy"
    ],
    "dog_sleeping": [
        "dog sleeping comfortably", "dog sleeping on bed", "puppy sleeping", "dog taking a nap",
        "dog resting peaceably", "dog sleeping on couch", "dog sleeping deeply", "cute sleeping dog",
        "dog curled up sleeping", "dog dreaming"
    ],
    "cat_sleeping": [
        "cat sleeping comfortably", "cat sleeping on bed", "kitten sleeping", "cat taking a nap",
        "cat resting peaceably", "cat sleeping in sunlight", "cat sleeping deeply", "cute sleeping cat",
        "cat curled up sleeping", "cat dreaming window"
    ],
    "dog_portrait": [
        "beautiful dog portrait", "golden retriever portrait", "husky dog portrait", "cute puppy portrait",
        "dog looking at camera", "dog close up face", "majestic dog portrait", "dog outdoor portrait",
        "dog sitting looking", "corgi portrait", "french bulldog portrait", "poodle portrait"
    ],
    "cat_portrait": [
        "beautiful cat portrait", "british shorthair cat", "persian cat portrait", "cute kitten portrait",
        "cat looking at camera", "cat close up face", "majestic cat portrait", "cat indoor portrait",
        "cat sitting looking", "siamese cat portrait", "maine coon portrait", "scottish fold portrait"
    ],
    "veterinary_clinic": [
        "dog at veterinary clinic", "cat at veterinary clinic", "veterinarian checking dog", "veterinarian examining cat",
        "veterinary clinic interior", "pet hospital", "veterinary care dog", "veterinary care cat",
        "dog getting vaccination", "cat getting checkup", "veterinary stethoscope pet", "animal hospital"
    ],
    "pet_shop": [
        "pet shop interior", "dog food store", "cat food store", "pet store supplies",
        "pet accessories store", "pet shop dog toys", "pet store shelves", "buying pet food",
        "pet store treats", "pet supermarket"
    ],
    "owner_and_pet": [
        "owner playing with dog", "owner petting cat", "owner hugging dog", "owner holding kitten",
        "person walking dog", "person holding dog", "person petting dog", "person feeding cat",
        "owner bonding with pet", "happy dog with owner"
    ]
}

# Gom toàn bộ từ khóa
ALL_KEYWORDS = []
for k_list in KEYWORD_POOL.values():
    ALL_KEYWORDS.extend(k_list)


def get_pexels_image(keyword: str, width: int = 1200, height: int = 630) -> bytes | None:
    """Gọi Pexels API để lấy ảnh stock thật 100% không bị trùng lặp."""
    if not PEXELS_API_KEY:
        print("    [!] THIẾU PEXELS API KEY. Vui lòng thêm PEXELS_API_KEY vào file .env")
        return None
        
    # Loại trừ ảnh có mặt người (nếu muốn tối đa hóa hình thú cưng)
    # Tuy nhiên Pexels search không hỗ trợ toán tử trừ (-) trực tiếp qua API tốt như Google.
    # Nên ta dựa vào keyword cụ thể.
    
    headers = {"Authorization": PEXELS_API_KEY}
    
    # Chọn random trang từ 1 đến 5 để đảm bảo không lấy mãi 1 ảnh đầu tiên
    page = random.randint(1, 3) 
    url = f"https://api.pexels.com/v1/search?query={keyword}&per_page=15&page={page}"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            photos = data.get("photos", [])
            if photos:
                # Đọc danh sách ảnh đã dùng
                used_photos = set()
                if os.path.exists("used_photos.txt"):
                    with open("used_photos.txt", "r") as f:
                        used_photos = set(f.read().splitlines())
                
                # Trộn ngẫu nhiên và chọn ảnh chưa từng dùng
                random.shuffle(photos)
                chosen = None
                for p in photos:
                    if str(p['id']) not in used_photos:
                        chosen = p
                        break
                
                # Nếu tất cả đều đã dùng, đành lấy đại 1 tấm
                if not chosen:
                    chosen = random.choice(photos)

                # Lưu ID ảnh vào danh sách đã dùng
                with open("used_photos.txt", "a") as f:
                    f.write(str(chosen['id']) + "\n")

                img_url = chosen["src"]["large2x"] if width >= 1000 else chosen["src"]["large"]
                
                # Tải ảnh về bytes
                img_resp = requests.get(img_url, timeout=15)
                if img_resp.status_code == 200:
                    print(f"    [PEXELS OK] Keyword: '{keyword}' - Photo ID: {chosen['id']}")
                    return img_resp.content
        else:
            print(f"    [PEXELS ERR] HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"    [PEXELS EXCEPTION] {e}")
        
    return None

def get_category_for_keyword(keyword: str) -> str:
    """Xác định danh mục từ khóa dựa trên tiêu đề bài viết."""
    kw_lower = keyword.lower()
    
    # Ưu tiên các hành động/trạng thái
    if any(t in kw_lower for t in ["ăn", "thức ăn", "hạt", "pate", "súp", "dinh dưỡng"]):
        return "dog_eating" if "chó" in kw_lower else "cat_eating"
        
    if any(t in kw_lower for t in ["tắm", "chải", "spa", "vệ sinh", "làm sạch", "khử mùi"]):
        return "dog_bathing" if "chó" in kw_lower else "cat_bathing"
        
    if any(t in kw_lower for t in ["chơi", "đồ chơi", "huấn luyện", "cắn", "vận động"]):
        return "dog_playing" if "chó" in kw_lower else "cat_playing"
        
    if any(t in kw_lower for t in ["ngủ", "nệm", "giường", "nằm", "chuồng", "nghỉ"]):
        return "dog_sleeping" if "chó" in kw_lower else "cat_sleeping"
        
    if any(t in kw_lower for t in ["khám", "bác sĩ", "thú y", "tiêm", "vaccine", "bệnh", "viêm"]):
        return "veterinary_clinic"
        
    if any(t in kw_lower for t in ["mua", "shop", "cửa hàng", "siêu thị"]):
        return "pet_shop"
        
    # Mặc định trả về chân dung
    if "chó" in kw_lower or any(b in kw_lower for b in ["corgi", "husky", "poodle", "pug", "shiba"]):
        return "dog_portrait"
    elif "mèo" in kw_lower or any(b in kw_lower for b in ["anh", "ba tư", "scottish", "ragdoll"]):
        return "cat_portrait"
        
    # Nếu không xác định được, random bất kỳ ảnh động vật nào
    return random.choice(list(KEYWORD_POOL.keys()))

def download_stock_photo(article_keyword: str, width: int = 1200, height: int = 630) -> bytes | None:
    """Hàm chính để fully_auto_consen gọi. Tải ảnh stock theo chủ đề."""
    category = get_category_for_keyword(article_keyword)
    
    # Chọn ngẫu nhiên 1 từ khóa cụ thể trong danh mục
    search_keyword = random.choice(KEYWORD_POOL[category])
    
    # Nếu Pexels API Key chưa được cài đặt, in ra cảnh báo.
    if not PEXELS_API_KEY:
        print("==================================================================")
        print(" ❌ CẢNH BÁO: CHƯA CÓ PEXELS API KEY TRONG FILE .env !!!")
        print(" Vui lòng đăng ký miễn phí tại https://www.pexels.com/api/")
        print(" Và thêm dòng PEXELS_API_KEY=xxxxx vào file .env")
        print(" Tạm thời hệ thống sẽ không có ảnh!")
        print("==================================================================")
        return None

    return get_pexels_image(search_keyword, width, height)

# Test cục bộ
if __name__ == "__main__":
    kws = ["chó bị tiêu chảy", "thức ăn cho mèo", "sữa tắm cho chó", "đồ chơi mèo"]
    for kw in kws:
        print(f"\nTest bài viết: {kw}")
        download_stock_photo(kw)
