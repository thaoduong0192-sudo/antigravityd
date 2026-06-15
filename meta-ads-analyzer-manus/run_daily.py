"""
run_daily.py
------------
Entry point chính — chạy mỗi ngày (qua Windows Task Scheduler).
Workflow:
  1. Auth + validate token
  2. Lấy campaigns
  3. Lấy insights hôm qua (hoặc date tùy chọn)
  4. Phân tích Messenger & Engagement
  5. Tạo báo cáo JSON
  6. Gửi alert nếu cần
"""

import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.auth import setup_connection
from core.api_client import MetaAdsClient
from analyzers.messenger_analyzer import analyze_messenger_campaigns
from analyzers.engagement_analyzer import analyze_engagement_campaigns
from analyzers.action_engine import execute_automated_actions
from reporters.alert_engine import collect_all_alerts, format_alert_summary, send_zalo_alert, save_alert_log
from reporters.daily_report import generate_daily_report, print_console_summary


def load_settings() -> dict:
    settings_file = PROJECT_ROOT / "config" / "settings.json"
    if not settings_file.exists():
        print("⚠️  Không tìm thấy config/settings.json, dùng defaults.")
        return {}
    with open(settings_file, "r", encoding="utf-8") as f:
        return json.load(f)


def run(date_preset: str = "yesterday", verbose: bool = False):
    print(f"\n🚀 Meta Ads Optimizer — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 50)

    # 1. Auth
    creds, accounts = setup_connection()
    settings = load_settings()
    report_dir = PROJECT_ROOT / "reports"

    all_messenger = []
    all_engagement = []
    all_actions = []
    account_overview = {}

    # 2. Process each Ad Account
    for account_info in accounts:
        if account_info.get("account_status") != 1:
            print(f"⚠️  Bỏ qua account {account_info['name']} — trạng thái: {account_info['status_label']}")
            continue

        account_id = account_info["id"]
        currency = account_info.get("currency", "VND")
        print(f"\n📊 Đang phân tích: {account_info['name']} ({account_id})")

        client = MetaAdsClient(account_id, currency)

        # Lấy danh sách campaigns
        campaigns = client.get_campaigns(status_filter=["ACTIVE"])
        if not campaigns:
            print("   ⚠️  Không có campaign ACTIVE nào")
            continue

        print(f"   📋 Tìm thấy {len(campaigns)} campaign ACTIVE")

        # Lấy insights
        # CBO campaigns → campaign level
        cbo_campaigns = [c for c in campaigns if c.get("is_cbo")]
        manual_campaigns = [c for c in campaigns if not c.get("is_cbo")]

        insights = []
        if cbo_campaigns:
            print(f"   🔀 {len(cbo_campaigns)} CBO campaigns → lấy Campaign level insights")
            campaign_insights = client.get_campaign_insights(date_preset=date_preset)
            insights.extend(campaign_insights)

        if manual_campaigns:
            print(f"   🔧 {len(manual_campaigns)} Manual campaigns → lấy Ad Set level insights")
            adset_insights = client.get_adset_insights(date_preset=date_preset)
            insights.extend(adset_insights)

        if verbose:
            print(f"   📥 Tổng {len(insights)} rows insights")

        # Phân tích
        messenger = analyze_messenger_campaigns(insights, campaigns, settings)
        engagement = analyze_engagement_campaigns(insights, campaigns, settings)

        print(f"   💬 Messenger Ads: {len(messenger)} entities")
        print(f"   👍 Engagement Ads: {len(engagement)} entities")
        
        # 2.5 Actions tự động hóa
        actions_taken = execute_automated_actions(client, messenger, engagement, settings)
        if actions_taken:
            all_actions.extend(actions_taken)

        all_messenger.extend(messenger)
        all_engagement.extend(engagement)
        account_overview = account_info

    # 3. Tạo alerts
    alerts = collect_all_alerts(all_messenger, all_engagement)

    # 4. Báo cáo
    date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if date_preset == "today":
        date_str = datetime.now().strftime("%Y-%m-%d")

    report_file = generate_daily_report(
        account_overview=account_overview,
        messenger_results=all_messenger,
        engagement_results=all_engagement,
        alerts=alerts,
        actions=all_actions,
        date_str=date_str,
        report_dir=report_dir,
    )

    # 5. Console summary
    with open(report_file, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    print_console_summary(report_data)

    # 6. Alert log
    save_alert_log(alerts, report_dir)

    # 7. Zalo alert
    if alerts.get("critical") or alerts.get("warning") or all_actions:
        alert_text = format_alert_summary(alerts, date_str)
        if all_actions:
            alert_text += f"\n\n⚡ TỰ ĐỘNG HÓA ({len(all_actions)} hành động):"
            for act in all_actions:
                alert_text += f"\n  - Đã {act['action']} {act['level'].upper()}: {act['name']} ({act['reason']})"
                
        sent = send_zalo_alert(alert_text, settings)
        if not sent and settings.get("zalo_alert", {}).get("enabled"):
            print("⚠️  Không gửi được Zalo alert")

    print(f"\n✅ Hoàn thành! Mở dashboard: dashboard/index.html")
    return report_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Meta Ads Daily Runner")
    parser.add_argument(
        "--date", default="yesterday",
        choices=["yesterday", "today", "last_7d", "last_30d"],
        help="Khoảng thời gian lấy data (default: yesterday)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="In thêm thông tin debug")
    args = parser.parse_args()

    run(date_preset=args.date, verbose=args.verbose)
