"""
breakdown_handler.py
--------------------
Áp dụng Breakdown Effect rules từ SKILL.md:
- CBO campaigns → evaluate at Campaign level
- Non-CBO (manual budget) → evaluate at Ad Set level
- NEVER recommend pause/reduce budget based solely on average CPA in breakdown reports
"""

from typing import Optional

# Ngưỡng judgment cho rankings
RANKING_SCORES = {
    "ABOVE_AVERAGE": 3,
    "AVERAGE": 2,
    "BELOW_AVERAGE": 1,
    None: 0,
    "": 0,
}

RANKING_LABELS = {
    "ABOVE_AVERAGE": "✅ Above average",
    "AVERAGE": "⚠️  Average",
    "BELOW_AVERAGE": "❌ Below average",
}


def detect_campaign_type(campaign_data: dict) -> str:
    """
    Phát hiện loại campaign để chọn evaluation level đúng.
    Returns: "CBO" hoặc "MANUAL"
    """
    # Nếu budget set ở level campaign → CBO
    if campaign_data.get("daily_budget") or campaign_data.get("lifetime_budget"):
        return "CBO"
    return "MANUAL"


def get_evaluation_level(campaign_data: dict) -> str:
    """
    SKILL.md rule:
    - CBO → Campaign level
    - Manual (non-CBO) → Ad Set level
    """
    campaign_type = detect_campaign_type(campaign_data)
    if campaign_type == "CBO":
        return "campaign"
    return "adset"


def evaluate_relevance_rankings(insight: dict) -> dict:
    """
    Đánh giá ad relevance diagnostics từ 3 ranking metrics.
    Returns dict với nhận xét và điểm tổng.
    """
    quality = insight.get("quality_ranking", "")
    conversion = insight.get("conversion_rate_ranking", "")
    engagement = insight.get("engagement_rate_ranking", "")

    quality_score = RANKING_SCORES.get(quality, 0)
    conversion_score = RANKING_SCORES.get(conversion, 0)
    engagement_score = RANKING_SCORES.get(engagement, 0)
    total_score = quality_score + conversion_score + engagement_score
    max_score = 9  # 3 × ABOVE_AVERAGE

    issues = []
    if quality_score <= 1:
        issues.append("Quality ranking thấp — nội dung ad cần cải thiện")
    if conversion_score <= 1:
        issues.append("Conversion rate ranking thấp — landing page hoặc offer cần xem lại")
    if engagement_score <= 1:
        issues.append("Engagement rate ranking thấp — creative cần A/B test")

    return {
        "quality_ranking": quality,
        "quality_label": RANKING_LABELS.get(quality, "N/A"),
        "conversion_rate_ranking": conversion,
        "conversion_label": RANKING_LABELS.get(conversion, "N/A"),
        "engagement_rate_ranking": engagement,
        "engagement_label": RANKING_LABELS.get(engagement, "N/A"),
        "total_score": total_score,
        "max_score": max_score,
        "health_pct": round((total_score / max_score) * 100, 1) if max_score > 0 else 0,
        "issues": issues,
    }


def check_creative_fatigue(insight: dict, settings: dict) -> Optional[str]:
    """
    Phát hiện creative fatigue dựa trên Frequency.
    KHÔNG recommend pause—chỉ recommend thay creative.
    """
    frequency = insight.get("frequency")
    if frequency is None:
        return None

    warn_threshold = settings.get("messenger_ads", {}).get("frequency_warning", 3.0)

    if frequency > warn_threshold:
        name = insight.get("ad_name") or insight.get("adset_name") or insight.get("campaign_name", "")
        return (
            f"Frequency = {frequency:.2f} (ngưỡng: {warn_threshold}) — "
            f"'{name}': Audience đang thấy quảng cáo quá nhiều lần. "
            f"Cân nhắc thay creative hoặc mở rộng audience."
        )
    return None


def breakdown_effect_warning(
    breakdown_data: list,
    evaluation_level: str,
) -> list:
    """
    Khi nhìn vào breakdown data (by placement, age, gender...), nếu một
    segment có average CPA cao hơn, ĐỪNG kết luận là system đang phân bổ sai.
    
    Trả về list cảnh báo có ngữ cảnh đúng về Breakdown Effect.
    """
    warnings = []
    if not breakdown_data:
        return warnings

    # Tìm segment có cost cao nhất và thấp nhất
    valid = [r for r in breakdown_data if r.get("cpm") is not None]
    if len(valid) < 2:
        return warnings

    sorted_by_cpm = sorted(valid, key=lambda x: x.get("cpm", 0))
    lowest = sorted_by_cpm[0]
    highest = sorted_by_cpm[-1]

    low_cpm = lowest.get("cpm", 0)
    high_cpm = highest.get("cpm", 0)

    if low_cpm > 0 and high_cpm / low_cpm > 2:
        warnings.append({
            "type": "BREAKDOWN_EFFECT",
            "message": (
                f"CPM khác biệt lớn giữa các segment ({low_cpm:.0f} vs {high_cpm:.0f}). "
                f"Đây có thể là Breakdown Effect — hệ thống Meta đang tối ưu marginal "
                f"efficiency, không phải average efficiency. "
                f"Đánh giá tại level: [{evaluation_level.upper()}]."
            ),
            "recommendation": (
                "KHÔNG pause segment CPM cao dựa trên average cost đơn thuần. "
                "Hãy xem xét total results và marginal cost của toàn campaign."
            )
        })

    return warnings
