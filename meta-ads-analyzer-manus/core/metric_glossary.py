"""
metric_glossary.py
------------------
Bảng mapping API field → tên chuẩn (Standardized display name) từ SKILL.md Manus.
Dùng để format tên metric trong mọi báo cáo và alert.
"""

# Mapping: API field → (standardized_name, definition)
METRIC_GLOSSARY = {
    "impressions": (
        "Impressions",
        "The number of times your ads were on screen."
    ),
    "reach": (
        "Reach",
        "The number of Accounts Center accounts that saw your ads at least once. "
        "Reach is different from impressions, which may include multiple views of "
        "your ads by the same Accounts Center accounts."
    ),
    "clicks": (
        "Clicks (all)",
        "The number of clicks, taps or swipes on your ads."
    ),
    "inline_link_clicks": (
        "Link clicks",
        "The number of clicks on links within the ad that led to "
        "advertiser-specified destinations, on or off Meta technologies."
    ),
    "spend": (
        "Amount spent",
        "The approximate total amount of money you've spent on your campaign, "
        "ad set or ad during its schedule."
    ),
    "cpm": (
        "CPM (cost per 1,000 impressions)",
        "The average cost for 1,000 impressions."
    ),
    "cpc": (
        "CPC (all)",
        "The average cost for each click (all)."
    ),
    "ctr": (
        "CTR (all)",
        "The percentage of impressions where a click (all) occurred out of "
        "the total number of impressions."
    ),
    "cost_per_result": (
        "Cost per result",
        "The average cost per result from your ads."
    ),
    "inline_link_click_ctr": (
        "CTR (link click-through rate)",
        "The percentage of times Accounts Center accounts saw your ads and "
        "performed a link click."
    ),
    "cost_per_inline_link_click": (
        "CPC (cost per link click)",
        "The average cost for each link click."
    ),
    # Messenger specific
    "actions:onsite_conversion.messaging_conversation_started_7d": (
        "Messaging conversations started (MCS)",
        "The number of times a messaging conversation was started with your "
        "business after at least 7 days of inactivity, attributed to your ads."
    ),
    "cost_per_mcs": (
        "Cost per MCS",
        "The average cost for each Messaging conversation started."
    ),
    # Video metrics
    "video_thruplay_watched_actions": (
        "ThruPlays",
        "The number of times your video was played to completion, "
        "or for at least 15 seconds."
    ),
    "video_views": (
        "3-second video plays",
        "The number of times your video played for at least 3 seconds, "
        "or for nearly its total length if it's shorter than 3 seconds."
    ),
    "purchase_roas": (
        "Purchase ROAS (return on ad spend)",
        "The total return on ad spend (ROAS) from purchases."
    ),
    "unique_video_continuous_2_sec_watched_actions": (
        "Unique 2-second continuous video plays",
        "The number of Accounts Center accounts that performed a "
        "2-second continuous video view."
    ),
    "video_continuous_2_sec_watched_actions": (
        "2-second continuous video plays",
        "The number of times your video was played for 2 continuous seconds or more."
    ),
    "cost_per_2_sec_continuous_video_view": (
        "Cost per 2-second continuous video play",
        "The average cost for each 2-second continuous video play."
    ),
    "video_30_sec_watched_actions": (
        "30-second video views",
        "The number of times your video played for at least 30 seconds."
    ),
    # Relevance rankings
    "quality_ranking": (
        "Quality ranking",
        "A ranking of your ad's perceived quality."
    ),
    "conversion_rate_ranking": (
        "Conversion rate ranking",
        "A ranking of your ad's expected conversion rate."
    ),
    "engagement_rate_ranking": (
        "Engagement rate ranking",
        "A ranking of your ad's expected engagement rate."
    ),
}

# API fields cần lấy cho Messenger Ads
MESSENGER_ADS_FIELDS = [
    "campaign_name", "campaign_id", "adset_name", "adset_id",
    "ad_name", "ad_id", "objective",
    "impressions", "reach", "clicks", "inline_link_clicks",
    "spend", "cpm", "cpc", "ctr", "inline_link_click_ctr",
    "cost_per_inline_link_click",
    "actions", "cost_per_action_type",
    "quality_ranking", "conversion_rate_ranking", "engagement_rate_ranking",
    "date_start", "date_stop",
]

# API fields cần lấy cho Engagement Ads
ENGAGEMENT_ADS_FIELDS = [
    "campaign_name", "campaign_id", "adset_name", "adset_id",
    "ad_name", "ad_id", "objective",
    "impressions", "reach", "clicks", "inline_link_clicks",
    "spend", "cpm", "cpc", "ctr",
    "actions", "cost_per_action_type",
    "video_views", "video_thruplay_watched_actions",
    "video_continuous_2_sec_watched_actions",
    "engagement_rate_ranking", "quality_ranking",
    "date_start", "date_stop",
]

# Forbidden terms (SKILL.md rule 1.1, 1.2)
FORBIDDEN_TERMS = ["people", "person", "users", "unique users", "clicks"]


def get_display_name(api_field: str) -> str:
    """Trả về tên chuẩn của metric. Dùng trong mọi báo cáo."""
    if api_field in METRIC_GLOSSARY:
        return METRIC_GLOSSARY[api_field][0]
    return api_field  # fallback


def get_definition(api_field: str) -> str:
    """Trả về định nghĩa chuẩn của metric."""
    if api_field in METRIC_GLOSSARY:
        return METRIC_GLOSSARY[api_field][1]
    return "Definition not available."


def format_currency(value, currency: str = "VND") -> str:
    """Format tiền tệ theo đúng rule SKILL.md."""
    if value is None:
        return "N/A"
    try:
        val = float(value)
        if currency == "VND":
            return f"{val:,.0f} VNĐ"
        else:
            return f"{val:.2f} {currency}"
    except (ValueError, TypeError):
        return "N/A"


def format_metric(api_field: str, value, currency: str = "VND") -> str:
    """Format giá trị metric với tên chuẩn."""
    name = get_display_name(api_field)
    if value is None:
        return f"{name}: Data not available"

    money_fields = ["spend", "cpm", "cpc", "cost_per_result",
                    "cost_per_inline_link_click", "cost_per_mcs"]
    pct_fields = ["ctr", "inline_link_click_ctr"]

    if api_field in money_fields:
        return f"{name}: {format_currency(value, currency)}"
    elif api_field in pct_fields:
        try:
            return f"{name}: {float(value):.2f}%"
        except (ValueError, TypeError):
            return f"{name}: N/A"
    else:
        return f"{name}: {value}"
