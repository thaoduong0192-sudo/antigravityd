import asyncio
from playwright.async_api import async_playwright

async def main():
    print("="*60)
    print(" CÔNG CỤ TẠO PHIÊN ĐĂNG NHẬP FACEBOOK (CHẠY 1 LẦN TRỌN ĐỜI)")
    print("="*60)
    print("Đang khởi tạo trình duyệt Chrome...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.facebook.com/")
        print("\n[HÀNH ĐỘNG CỦA BẠN]:")
        print("1. Trình duyệt đã mở Facebook.")
        print("2. Vui lòng đăng nhập vào tài khoản Facebook đang nắm quyền Admin trang 'viethoikyonline'.")
        print("3. Đợi trang facebook tải xong Newsfeed cá nhân hoàn tất.")
        
        input("\n[XÁC NHẬN]: Sau khi đã làm xong Bước 3, BẤM TRỰC TIẾP PHÍM ENTER VÀO CỬA SỔ CMD NÀY ĐỂ LƯU SESSION...")
        
        await context.storage_state(path="fb_session.json")
        print("✅ ĐÃ LƯU THÀNH CÔNG SESSION VÀO 'fb_session.json'!")
        print("Từ giờ trở đi, Bot có thể đăng tải ngầm lên Fanpage hoàn toàn tự động.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
