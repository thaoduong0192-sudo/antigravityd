"""
messenger_analyzer.py
---------------------
Phân tích chiến dịch Messenger Ads (objective: MESSAGES).
KPIs cốt lõi: Cost per MCS, CTR, CPM, Learning Phase, Ad Relevance.
"""

from typing import Optional
from analyzers.breakdown_handler import evaluate_relevance_rankings, check_creative_fatigue, get_evaluation_level


def analyze_messenger_campaigns(
    insights: list,
    campaigns_meta: list,
    settings: dict,
) -> list:
    """
    Phân tích toàn bộ Messenger Ads, trả về list kết quả phân tích mỗi entity.
    
    insights: output từ api_client (campaign hoặc adset level)
    campaigns_meta: danh sách campaign từ get_campaigns()
    settings: config/settings.json
    """
    threshold = settings.get("messenger_ads", {})
    campaign_map = {c["id"]: c for c in campaigns_meta}

    results = []
    for row in insights:
        obj = (row.get("objective") or "").upper()
        # Chỉ phân tích Messenger Ads
        if "MESSAGES" not in obj and "OUTCOME_ENGAGEMENT" not in obj:
            # Vẫn check nếu có MCS dù objective khác
            if not row.get("mcs"):
                continue

        campaign_id = row.get("campaign_id") or ""
        campaign_meta = campaign_map.get(campaign_id, {})
        eval_level = get_evaluation_level(campaign_meta)

        analysis = _analyze_single_row(row, threshold, eval_level)
        results.append(analysis)

    return results


def _analyze_single_row(row: dict, threshold: dict, eval_level: str) -> dict:
    """Phân tích một row insight Messenger Ad."""
    spend = row.get("spend") or 0
    mcs = row.get("mcs") or 0
    cost_per_mcs = row.get("cost_per_mcs")
    impressions = row.get("impressions") or 0
    cpm = row.get("cpm") or 0
    ctr_all = row.get("ctr_all") or 0
    frequency = row.get("frequency")
    currency = row.get("currency", "VND")

    alerts = []
    recommendations = []

    # ── RULE: Cost per MCS ──────────────────────────────────────────────────
    cpm_warn = threshold.get("cost_per_mcs_warning", 15000)
    cpm_crit = threshold.get("cost_per_mcs_critical", 25000)
    cpm_status = "ok"

    if cost_per_mcs is not None:
        if cost_per_mcs >= cpm_crit:
            cpm_status = "critical"
            alerts.append({
                "level": "CRITICAL",
                "metric": "Cost per MCS",
                "value": cost_per_mcs,
                "threshold": cpm_crit,
                "message": f"Cost per MCS = {cost_per_mcs:,.0f} {currency} vượt ngưỡng nguy hiểm {cpm_crit:,.0f} {currency}",
            })
            recommendations.append("Xem lại creative, offer, hoặc audience targeting. Kiểm tra ad relevance rankings.")
        elif cost_per_mcs >= cpm_warn:
            cpm_status = "warning"
            alerts.append({
                "level": "WARNING",
                "metric": "Cost per MCS",
                "value": cost_per_mcs,
                "threshold": cpm_warn,
                "message": f"Cost per MCS = {cost_per_mcs:,.0f} {currency} vượt ngưỡng cảnh báo {cpm_warn:,.0f} {currency}",
            })
            recommendations.append("Theo dõi thêm 1-2 ngày. Nếu tiếp tục tăng, cân nhắc refresh creative.")

    # ── RULE: CTR (all) ──────────────────────────────────────────────────────
    ctr_warn = threshold.get("ctr_all_warning", 1.0)
    ctr_crit = threshold.get("ctr_all_critical", 0.5)
    ctr_status = "ok"

    if ctr_all is not None:
        if ctr_all < ctr_crit:
            ctr_status = "critical"
            alerts.append({
                "level": "CRITICAL",
                "metric": "CTR (all)",
                "value": ctr_all,
                "threshold": ctr_crit,
                "message": f"CTR (all) = {ctr_all:.2f}% rất thấp (ngưỡng: {ctr_crit}%)",
            })
            recommendations.append("Creative không đủ hấp dẫn. Cần test headline và hình ảnh mới.")
        elif ctr_all < ctr_warn:
            ctr_status = "warning"
            alerts.append({
                "level": "WARNING",
                "metric": "CTR (all)",
                "value": ctr_all,
                "threshold": ctr_warn,
                "message": f"CTR (all) = {ctr_all:.2f}% thấp hơn mức khuyến nghị {ctr_warn}%",
            })

    # ── RULE: CPM ───────────────────────────────────────────────────────────
    cpm_w = threshold.get("cpm_warning", 80000)
    cpm_c = threshold.get("cpm_critical", 120000)
    cpm_status_label = "ok"

    if cpm:
        if cpm >= cpm_c:
            cpm_status_label = "critical"
            alerts.append({
                "level": "CRITICAL",
                "metric": "CPM (cost per 1,000 impressions)",
                "value": cpm,
                "threshold": cpm_c,
                "message": f"CPM = {cpm:,.0f} {currency} rất cao (ngưỡng: {cpm_c:,.0f})",
            })
            recommendations.append("Audience quá saturated hoặc quảng cáo không competitive. Mở rộng audience hoặc tăng chất lượng creative.")
        elif cpm >= cpm_w:
            cpm_status_label = "warning"
            alerts.append({
                "level": "WARNING",
                "metric": "CPM (cost per 1,000 impressions)",
                "value": cpm,
                "threshold": cpm_w,
                "message": f"CPM = {cpm:,.0f} {currency} đang tăng cao",
            })

    # ── RULE: Ad Relevance Diagnostics ───────────────────────────────────────
    relevance = evaluate_relevance_rankings(row)
    if relevance["issues"]:
        for issue in relevance["issues"]:
            alerts.append({
                "level": "WARNING",
                "metric": "Ad Relevance",
                "message": issue,
            })

    # ── RULE: Frequency / Creative Fatigue ──────────────────────────────────
    fatigue_warning = check_creative_fatigue(row, {"messenger_ads": threshold})
    if fatigue_warning:
        alerts.append({
            "level": "WARNING",
            "metric": "Frequency",
            "value": frequency,
            "message": fatigue_warning,
        })
        recommendations.append("Thêm creative variation mới hoặc expand audience.")

    # ── SCORE ────────────────────────────────────────────────────────────────
    score = _calculate_health_score(alerts)

    return {
        "type": "MESSENGER",
        "evaluation_level": eval_level,
        "campaign_id": row.get("campaign_id"),
        "campaign_name": row.get("campaign_name"),
        "adset_id": row.get("adset_id"),
        "adset_name": row.get("adset_name"),
        "ad_id": row.get("ad_id"),
        "ad_name": row.get("ad_name"),
        "date_start": row.get("date_start"),
        "date_stop": row.get("date_stop"),
        "currency": currency,
        # Core KPIs
        "spend": spend,
        "impressions": impressions,
        "reach": row.get("reach"),
        "frequency": frequency,
        "mcs": mcs,
        "cost_per_mcs": cost_per_mcs,
        "ctr_all": ctr_all,
        "cpm": cpm,
        "clicks_all": row.get("clicks_all"),
        "link_clicks": row.get("link_clicks"),
        # Relevance
        "relevance": relevance,
        # Alerts & Recommendations
        "alerts": alerts,
        "recommendations": list(set(recommendations)),  # dedupe
        "health_score": score,
        "health_label": _score_label(score),
    }


def _calculate_health_score(alerts: list) -> int:
    """0–100 score dựa trên số và severity của alerts."""
    score = 100
    for alert in alerts:
        if alert["level"] == "CRITICAL":
            score -= 25
        elif alert["level"] == "WARNING":
            score -= 10
    return max(0, score)


def _score_label(score: int) -> str:
    if score >= 80:
        return "🟢 Healthy"
    elif score >= 50:
        return "🟡 Needs Attention"
    else:
        return "🔴 Critical"
