"""
daily_report.py
---------------
Tạo báo cáo hàng ngày dưới dạng JSON + text summary.
Dữ liệu JSON sau đó được dashboard/index.html đọc để hiển thị.
"""

import json
from datetime import datetime
from pathlib import Path


def generate_daily_report(
    account_overview: dict,
    messenger_results: list,
    engagement_results: list,
    alerts: dict,
    actions: list,
    date_str: str,
    report_dir: Path,
) -> Path:
    """
    Tạo file JSON báo cáo ngày.
    Returns: Path đến file JSON đã tạo.
    """
    report_dir.mkdir(parents=True, exist_ok=True)

    # Tổng hợp spending
    total_spend_messenger = sum(r.get("spend", 0) or 0 for r in messenger_results)
    total_spend_engagement = sum(r.get("spend", 0) or 0 for r in engagement_results)
    total_mcs = sum(r.get("mcs", 0) or 0 for r in messenger_results)
    total_engagement = sum(r.get("post_engagement", 0) or 0 for r in engagement_results)

    # Overall health
    all_scores = [r.get("health_score", 100) for r in messenger_results + engagement_results]
    avg_health = round(sum(all_scores) / len(all_scores), 1) if all_scores else 100

    report = {
        "generated_at": datetime.now().isoformat(),
        "report_date": date_str,
        "account": {
            "id": account_overview.get("id"),
            "name": account_overview.get("name"),
            "currency": account_overview.get("currency", "VND"),
        },
        "summary": {
            "total_spend": total_spend_messenger + total_spend_engagement,
            "total_spend_messenger": total_spend_messenger,
            "total_spend_engagement": total_spend_engagement,
            "total_mcs": total_mcs,
            "total_engagement": total_engagement,
            "avg_cost_per_mcs": (total_spend_messenger / total_mcs) if total_mcs > 0 else None,
            "messenger_campaigns_count": len(messenger_results),
            "engagement_campaigns_count": len(engagement_results),
            "avg_health_score": avg_health,
            "critical_alerts": len(alerts.get("critical", [])),
            "warning_alerts": len(alerts.get("warning", [])),
        },
        "messenger_campaigns": messenger_results,
        "engagement_campaigns": engagement_results,
        "alerts": alerts,
        "automated_actions": actions,
    }

    output_file = report_dir / f"report_{date_str}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    print(f"✅ Báo cáo đã lưu: {output_file}")

    # Tạo symlink/copy thành report_latest.json cho dashboard
    latest_file = report_dir / "report_latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    return output_file


def print_console_summary(report: dict):
    """In tóm tắt ra console."""
    summary = report.get("summary", {})
    currency = report.get("account", {}).get("currency", "VND")
    date_str = report.get("report_date", "N/A")

    print("\n" + "=" * 50)
    print(f"📊 BÁO CÁO META ADS — {date_str}")
    print("=" * 50)
    print(f"💰 Tổng chi tiêu: {summary.get('total_spend', 0):,.0f} {currency}")
    print(f"   ├── Messenger Ads: {summary.get('total_spend_messenger', 0):,.0f} {currency}")
    print(f"   └── Engagement Ads: {summary.get('total_spend_engagement', 0):,.0f} {currency}")
    print(f"\n💬 Tổng MCS: {summary.get('total_mcs', 0):,.0f}")

    avg_mcs = summary.get("avg_cost_per_mcs")
    if avg_mcs:
        print(f"📩 Cost per MCS: {avg_mcs:,.0f} {currency}")

    print(f"\n👍 Tổng Engagement: {summary.get('total_engagement', 0):,.0f}")
    print(f"❤️  Health Score tb: {summary.get('avg_health_score', 0)}/100")

    critical = summary.get("critical_alerts", 0)
    warnings = summary.get("warning_alerts", 0)
    if critical > 0:
        print(f"\n🔴 {critical} vấn đề CRITICAL cần xử lý ngay!")
    if warnings > 0:
        print(f"🟡 {warnings} cảnh báo WARNING")
    if critical == 0 and warnings == 0:
        print("\n✅ Tất cả chiến dịch hoạt động bình thường!")
        
    actions = report.get("automated_actions", [])
    if actions:
        print(f"\n⚡ Đã thực thi {len(actions)} hành động tự động:")
        for act in actions:
            print(f"   ➤ {act['action']} {act['level'].upper()} '{act['name']}' - {act['reason']}")
            
    print("=" * 50)
