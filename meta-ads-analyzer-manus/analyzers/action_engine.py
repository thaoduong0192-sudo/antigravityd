"""
action_engine.py
----------------
Xử lý các hành động tự động hóa dựa trên ngưỡng thiết lập trong settings.
Bao gồm: tự động tắt campaign/adset không hiệu quả, tự động tăng ngân sách.
"""

from typing import List, Dict, Any
from core.api_client import MetaAdsClient

def execute_automated_actions(client: MetaAdsClient, messenger_data: List[Dict], engagement_data: List[Dict], settings: Dict) -> List[Dict]:
    executed_actions = []
    
    auto_settings = settings.get("auto_actions", {})
    if not auto_settings.get("enabled", False):
        return executed_actions

    ms_rules = auto_settings.get("messenger_rules", {})
    eg_rules = auto_settings.get("engagement_rules", {})

    print("\n⚡ [ACTION ENGINE] Kiểm tra các quy tắc tự động hóa...")

    # 1. Quét Messenger Campaigns
    for item in messenger_data:
        cpmcs = item.get("cost_per_mcs")
        pause_thresh = ms_rules.get("auto_pause_mcs_cost_greater_than")
        if cpmcs and pause_thresh and cpmcs > pause_thresh:
            reason = f"Cost/MCS ({cpmcs}) > {pause_thresh}"
            # Only pause if not already paused (mocking check conceptually)
            if _try_pause(client, item, reason):
                executed_actions.append({
                    "level": item["level"],
                    "id": item.get("campaign_id") if item["level"] == "campaign" else item.get("adset_id"),
                    "name": item.get("campaign_name") if item["level"] == "campaign" else item.get("adset_name"),
                    "action": "PAUSED",
                    "reason": reason
                })

    # 2. Xử lý Engagement Campaigns
    for item in engagement_data:
        cpe = item.get("cpe")
        pause_thresh = eg_rules.get("auto_pause_cpe_greater_than")
        if cpe and pause_thresh and cpe > pause_thresh:
            reason = f"CPE ({cpe}) > {pause_thresh}"
            if _try_pause(client, item, reason):
                executed_actions.append({
                    "level": item["level"],
                    "id": item.get("campaign_id") if item["level"] == "campaign" else item.get("adset_id"),
                    "name": item.get("campaign_name") if item["level"] == "campaign" else item.get("adset_name"),
                    "action": "PAUSED",
                    "reason": reason
                })

    print(f"⚡ [ACTION ENGINE] Đã thực thi {len(executed_actions)} hành động.")
    return executed_actions


def _try_pause(client: MetaAdsClient, item: dict, reason: str) -> bool:
    level = item.get("level")
    success = False
    
    if level == "campaign":
        camp_id = item.get("campaign_id")
        if camp_id:
            print(f"   🚫 Hành động xử lý: Tắt Campaign {camp_id} ({item.get('campaign_name')}) - Lý do: {reason}")
            success = client.update_campaign_status(camp_id, "PAUSED")
    elif level == "adset":
        adset_id = item.get("adset_id")
        if adset_id:
            print(f"   🚫 Hành động xử lý: Tắt AdSet {adset_id} ({item.get('adset_name')}) - Lý do: {reason}")
            success = client.update_adset_status(adset_id, "PAUSED")
            
    return success
