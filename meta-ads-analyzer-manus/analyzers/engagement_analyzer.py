"""
engagement_analyzer.py
----------------------
Phân tích chiến dịch Engagement Ads (objective: POST_ENGAGEMENT, REACH...).
KPIs: CPE, Frequency, Engagement Rate, Creative Fatigue.
"""

from analyzers.breakdown_handler import evaluate_relevance_rankings, check_creative_fatigue, get_evaluation_level


def analyze_engagement_campaigns(
    insights: list,
    campaigns_meta: list,
    settings: dict,
) -> list:
    """Phân tích Engagement Ads, trả về list kết quả."""
    threshold = settings.get("engagement_ads", {})
    campaign_map = {c["id"]: c for c in campaigns_meta}
    results = []

    for row in insights:
        obj = (row.get("objective") or "").upper()
        engagement_obj = {"POST_ENGAGEMENT", "PAGE_LIKES", "REACH",
                          "VIDEO_VIEWS", "OUTCOME_ENGAGEMENT"}
        if not any(o in obj for o in engagement_obj):
            # Vẫn check nếu có post_engagement data
            if not row.get("post_engagement"):
                continue

        campaign_id = row.get("campaign_id") or ""
        campaign_meta = campaign_map.get(campaign_id, {})
        eval_level = get_evaluation_level(campaign_meta)

        analysis = _analyze_single_row(row, threshold, eval_level)
        results.append(analysis)

    return results


def _analyze_single_row(row: dict, threshold: dict, eval_level: str) -> dict:
    spend = row.get("spend") or 0
    impressions = row.get("impressions") or 0
    reach = row.get("reach") or 0
    frequency = row.get("frequency")
    post_engagement = row.get("post_engagement") or 0
    cpe = row.get("cpe")
    ctr_all = row.get("ctr_all") or 0
    currency = row.get("currency", "VND")

    # Engagement rate = engagement / reach (%)
    engagement_rate = (post_engagement / reach * 100) if reach > 0 else None

    alerts = []
    recommendations = []

    # ── RULE: CPE (Cost per Engagement) ─────────────────────────────────────
    cpe_warn = threshold.get("cpe_warning", 500)
    cpe_crit = threshold.get("cpe_critical", 1000)

    if cpe is not None:
        if cpe >= cpe_crit:
            alerts.append({
                "level": "CRITICAL",
                "metric": "CPE",
                "value": cpe,
                "threshold": cpe_crit,
                "message": f"CPE = {cpe:,.0f} {currency} quá cao (ngưỡng: {cpe_crit:,.0f})",
            })
            recommendations.append("Chi phí tương tác quá cao. Xem lại creative và audience targeting.")
        elif cpe >= cpe_warn:
            alerts.append({
                "level": "WARNING",
                "metric": "CPE",
                "value": cpe,
                "threshold": cpe_warn,
                "message": f"CPE = {cpe:,.0f} {currency} vượt ngưỡng cảnh báo",
            })

    # ── RULE: Frequency / Creative Fatigue ──────────────────────────────────
    freq_warn = threshold.get("frequency_warning", 3.5)
    if frequency and frequency > freq_warn:
        alerts.append({
            "level": "WARNING",
            "metric": "Frequency",
            "value": frequency,
            "threshold": freq_warn,
            "message": f"Frequency = {frequency:.2f} — audience đã thấy ad quá nhiều lần",
        })
        recommendations.append("Thêm creative mới hoặc mở rộng audience để giảm frequency.")

    # ── RULE: Engagement Rate ────────────────────────────────────────────────
    er_warn = threshold.get("engagement_rate_warning", 1.0)
    if engagement_rate is not None and engagement_rate < er_warn:
        alerts.append({
            "level": "WARNING",
            "metric": "Engagement Rate",
            "value": engagement_rate,
            "threshold": er_warn,
            "message": f"Engagement Rate = {engagement_rate:.2f}% thấp (ngưỡng: {er_warn}%)",
        })
        recommendations.append("Nội dung không đủ hấp dẫn với audience này. Thử nội dung emotional hoặc câu hỏi.")

    # ── RULE: Engagement Rate Ranking ────────────────────────────────────────
    relevance = evaluate_relevance_rankings(row)
    er_ranking = row.get("engagement_rate_ranking", "")
    if er_ranking == "BELOW_AVERAGE":
        alerts.append({
            "level": "WARNING",
            "metric": "Engagement rate ranking",
            "message": "Engagement rate ranking thấp hơn mức trung bình — cần A/B test content",
        })
        recommendations.append("Thử A/B test content: emotional hook, câu hỏi, hoặc video ngắn.")

    # ── RULE: CTR ────────────────────────────────────────────────────────────
    ctr_warn = threshold.get("ctr_all_warning", 0.5)
    if ctr_all < ctr_warn:
        alerts.append({
            "level": "WARNING",
            "metric": "CTR (all)",
            "value": ctr_all,
            "threshold": ctr_warn,
            "message": f"CTR (all) = {ctr_all:.2f}% thấp",
        })

    score = _calculate_health_score(alerts)

    return {
        "type": "ENGAGEMENT",
        "evaluation_level": eval_level,
        "campaign_id": row.get("campaign_id"),
        "campaign_name": row.get("campaign_name"),
        "adset_id": row.get("adset_id"),
        "adset_name": row.get("adset_name"),
        "date_start": row.get("date_start"),
        "date_stop": row.get("date_stop"),
        "currency": currency,
        # Core KPIs
        "spend": spend,
        "impressions": impressions,
        "reach": reach,
        "frequency": frequency,
        "post_engagement": post_engagement,
        "cpe": cpe,
        "engagement_rate": engagement_rate,
        "ctr_all": ctr_all,
        # Relevance
        "relevance": relevance,
        # Results
        "alerts": alerts,
        "recommendations": list(set(recommendations)),
        "health_score": score,
        "health_label": _score_label(score),
    }


def _calculate_health_score(alerts: list) -> int:
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
