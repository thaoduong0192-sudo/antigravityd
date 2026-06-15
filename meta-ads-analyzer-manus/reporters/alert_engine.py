"""
alert_engine.py
---------------
Phát hiện anomaly và gửi cảnh báo.
- Tổng hợp alerts từ tất cả analyzer results
- Phân loại: CRITICAL / WARNING / INFO
- Tích hợp Zalo bot (nếu được bật trong settings)
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


def collect_all_alerts(
    messenger_results: list,
    engagement_results: list,
) -> dict:
    """
    Tổng hợp tất cả alerts từ các analyzer.
    Returns dict: {critical: [], warning: [], info: []}
    """
    critical = []
    warning = []
    info = []

    all_results = messenger_results + engagement_results
    for result in all_results:
        entity_name = (
            result.get("ad_name")
            or result.get("adset_name")
            or result.get("campaign_name")
            or "Unknown"
        )
        entity_type = result.get("type", "")
        spend = result.get("spend", 0)
        currency = result.get("currency", "VND")

        for alert in result.get("alerts", []):
            enriched = {
                **alert,
                "entity_name": entity_name,
                "entity_type": entity_type,
                "campaign_name": result.get("campaign_name"),
                "spend": spend,
                "currency": currency,
                "health_score": result.get("health_score"),
            }
            if alert["level"] == "CRITICAL":
                critical.append(enriched)
            elif alert["level"] == "WARNING":
                warning.append(enriched)
            else:
                info.append(enriched)

        # Low health score → auto INFO
        health_score = result.get("health_score", 100)
        if health_score < 50 and not any(
            a.get("entity_name") == entity_name and a.get("level") == "CRITICAL"
            for a in critical
        ):
            info.append({
                "level": "INFO",
                "entity_name": entity_name,
                "entity_type": entity_type,
                "campaign_name": result.get("campaign_name"),
                "message": f"Health score thấp: {health_score}/100 — {result.get('health_label', '')}",
                "spend": spend,
                "currency": currency,
            })

    return {"critical": critical, "warning": warning, "info": info}


def format_alert_summary(alerts: dict, date_str: str = None) -> str:
    """Format text summary dùng cho Zalo/log."""
    date_str = date_str or datetime.now().strftime("%d/%m/%Y")
    lines = [f"📊 BÁO CÁO META ADS — {date_str}"]
    lines.append("=" * 40)

    critical = alerts.get("critical", [])
    warning = alerts.get("warning", [])
    info = alerts.get("info", [])

    if not critical and not warning:
        lines.append("✅ Tất cả chiến dịch hoạt động bình thường!")
    else:
        if critical:
            lines.append(f"\n🔴 CRITICAL ({len(critical)} vấn đề):")
            for a in critical[:5]:  # max 5 alerts hiển thị
                lines.append(f"  • [{a.get('entity_name', '')}] {a.get('message', '')}")
            if len(critical) > 5:
                lines.append(f"  ... và {len(critical)-5} vấn đề khác")

        if warning:
            lines.append(f"\n🟡 WARNING ({len(warning)} cảnh báo):")
            for a in warning[:5]:
                lines.append(f"  • [{a.get('entity_name', '')}] {a.get('message', '')}")
            if len(warning) > 5:
                lines.append(f"  ... và {len(warning)-5} cảnh báo khác")

    if info:
        lines.append(f"\nℹ️  INFO: {len(info)} thông tin thêm")

    lines.append("\n📱 Xem chi tiết: mở dashboard/index.html")
    return "\n".join(lines)


def send_zalo_alert(message: str, settings: dict) -> bool:
    """
    Gửi alert qua Zalo bot.
    Dùng zalo_bu_agent.py đã có trong D:\Antigravity nếu được cấu hình.
    """
    zalo_config = settings.get("zalo_alert", {})
    if not zalo_config.get("enabled", False):
        return False

    phone = zalo_config.get("phone_number", "")
    if not phone:
        print("⚠️  Zalo alert bật nhưng chưa có phone_number trong settings.json")
        return False

    zalo_agent_path = Path(__file__).parent.parent.parent / "zalo_bu_agent.py"
    if not zalo_agent_path.exists():
        print(f"⚠️  Không tìm thấy zalo_bu_agent.py tại {zalo_agent_path}")
        return False

    try:
        # Ghi message vào temp file để tránh encoding issues với cmd
        temp_msg_file = Path(__file__).parent.parent / "reports" / "_temp_zalo_msg.txt"
        temp_msg_file.parent.mkdir(exist_ok=True)
        with open(temp_msg_file, "w", encoding="utf-8") as f:
            f.write(message)

        result = subprocess.run(
            ["python", str(zalo_agent_path),
             "--phone", phone,
             "--message-file", str(temp_msg_file)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            print("✅ Đã gửi Zalo alert")
            return True
        else:
            print(f"⚠️  Zalo alert lỗi: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"⚠️  Không gửi được Zalo alert: {e}")
        return False


def save_alert_log(alerts: dict, report_dir: Path):
    """Lưu alerts vào file log JSON."""
    report_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = report_dir / f"alerts_{date_str}.json"

    log_data = {
        "generated_at": datetime.now().isoformat(),
        "date": date_str,
        "summary": {
            "critical_count": len(alerts.get("critical", [])),
            "warning_count": len(alerts.get("warning", [])),
            "info_count": len(alerts.get("info", [])),
        },
        "alerts": alerts,
    }

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2, default=str)

    print(f"✅ Đã lưu alert log: {log_file}")
    return log_file
