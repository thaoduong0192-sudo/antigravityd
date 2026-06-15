import os
import sys
import json
import requests
import base64
from win10toast import ToastNotifier

# Fix encoding issues when running from task scheduler
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(DIR_PATH, "last_orders.json")

# Credentials for helloconsen
HC_USER = "adminai"
HC_PASS = "pgtm hxFR 1HRe mmNB ew5f dEvp"
HC_TOKEN = base64.b64encode(f"{HC_USER}:{HC_PASS}".encode()).decode()

# Credentials for ecopets
EP_USER = "ecopets"
EP_PASS = "nOz7 a3KK iWhD KLyu w0vX UL1m"
EP_TOKEN = base64.b64encode(f"{EP_USER}:{EP_PASS}".encode()).decode()

SITES = {
    "helloconsen.com": {
        "url": "https://helloconsen.com/wp-json/wc/v3/orders",
        "auth": HC_TOKEN
    },
    "ecopets.vn": {
        "url": "https://ecopets.vn/wp-json/wc/v3/orders",
        "auth": EP_TOKEN
    }
}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"helloconsen.com": 0, "ecopets.vn": 0}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)

def get_latest_orders(site, auth, last_id):
    headers = {"Authorization": f"Basic {auth}"}
    try:
        r = requests.get(f"{SITES[site]['url']}?per_page=10", headers=headers, timeout=10)
        if r.status_code == 200:
            orders = r.json()
            new_orders = []
            for order in orders:
                if order['id'] > last_id:
                    new_orders.append(order)
            return new_orders
    except Exception as e:
        print(f"Error fetching orders from {site}: {e}")
    return []

def main():
    state = load_state()
    toaster = ToastNotifier()
    
    found_new = False
    
    # First run initialization (don't alert on existing orders, just save the state)
    is_first_run = (state["helloconsen.com"] == 0 and state["ecopets.vn"] == 0)
    
    for site, config in SITES.items():
        last_id = state.get(site, 0)
        new_orders = get_latest_orders(site, config["auth"], last_id)
        
        if new_orders:
            # Sort chronologically (oldest to newest) to process properly
            new_orders.sort(key=lambda x: x['id'])
            for order in new_orders:
                o_id = order['id']
                
                if not is_first_run:
                    total = order.get('total', '0')
                    status = order.get('status', 'unknown')
                    billing = order.get('billing', {})
                    first_name = billing.get('first_name', '')
                    last_name = billing.get('last_name', '')
                    msg = f"Đơn hàng #{o_id} ({status})\nKhách: {first_name} {last_name}\nTổng: {total} VNĐ"
                    
                    try:
                        toaster.show_toast(
                            f"Có Đơn Mới trên {site}!",
                            msg,
                            duration=10,
                            threaded=False
                        )
                    except Exception as e:
                        print(f"Lỗi hiển thị Toast: {e}")
                
                state[site] = max(state[site], o_id)
                found_new = True
                
    if found_new:
        save_state(state)
        
if __name__ == "__main__":
    main()
