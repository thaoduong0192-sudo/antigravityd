"""
api_client.py
-------------
Facebook Graph API wrapper.
- Lấy insights cho Campaign / Ad Set / Ad level
- Xử lý actions array (Messaging conversations started)
- Áp dụng đúng level theo Breakdown Effect rule
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adset import AdSet
    from facebook_business.adobjects.ad import Ad
    from facebook_business.exceptions import FacebookRequestError
except ImportError:
    raise ImportError("Thiếu thư viện facebook-business. Chạy: pip install -r requirements.txt")

from core.metric_glossary import MESSENGER_ADS_FIELDS, ENGAGEMENT_ADS_FIELDS


# ── OBJECTIVES MAPPING ──────────────────────────────────────────────────────
MESSENGER_OBJECTIVES = {
    "MESSAGES", "OUTCOME_ENGAGEMENT"  # các objective liên quan Messenger
}
ENGAGEMENT_OBJECTIVES = {
    "POST_ENGAGEMENT", "PAGE_LIKES", "OUTCOME_ENGAGEMENT",
    "REACH", "VIDEO_VIEWS"
}
CBO_BUDGET_TYPES = {"CAMPAIGN"}  # CBO flag


def _parse_actions(actions_list: list, action_type: str) -> Optional[float]:
    """Extract giá trị từ actions array theo action_type."""
    if not actions_list:
        return None
    for action in actions_list:
        if action.get("action_type") == action_type:
            return float(action.get("value", 0))
    return None


def _parse_cost_per_action(cost_list: list, action_type: str) -> Optional[float]:
    """Extract cost_per_action_type theo action_type."""
    if not cost_list:
        return None
    for item in cost_list:
        if item.get("action_type") == action_type:
            return float(item.get("value", 0))
    return None


def _safe_float(value) -> Optional[float]:
    """Convert value sang float, trả None nếu không convert được."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class MetaAdsClient:
    """
    Client để lấy dữ liệu từ Meta Ads API.
    Áp dụng Breakdown Effect rules từ SKILL.md.
    """

    def __init__(self, ad_account_id: str, currency: str = "VND"):
        self.account_id = ad_account_id
        self.currency = currency
        self.account = AdAccount(ad_account_id)

    # ── CAMPAIGN LIST ────────────────────────────────────────────────────────
    def get_campaigns(self, status_filter: list = None) -> list:
        """
        Lấy danh sách campaigns trong account.
        status_filter: ["ACTIVE", "PAUSED"] — mặc định chỉ lấy ACTIVE
        """
        if status_filter is None:
            status_filter = ["ACTIVE"]

        params = {
            "effective_status": status_filter,
            "fields": "id,name,objective,status,budget_remaining,"
                      "daily_budget,lifetime_budget,buying_type,"
                      "bid_strategy,pacing_type",
        }

        try:
            campaigns = self.account.get_campaigns(params=params)
            result = []
            for c in campaigns:
                is_cbo = c.get("daily_budget") is not None or c.get("lifetime_budget") is not None
                result.append({
                    "id": c["id"],
                    "name": c["name"],
                    "objective": c.get("objective", "UNKNOWN"),
                    "status": c.get("status", "UNKNOWN"),
                    "is_cbo": is_cbo,
                    "daily_budget": _safe_float(c.get("daily_budget")),
                    "lifetime_budget": _safe_float(c.get("lifetime_budget")),
                    "bid_strategy": c.get("bid_strategy", "UNKNOWN"),
                })
            return result
        except FacebookRequestError as e:
            print(f"❌ Lỗi get_campaigns ({self.account_id}): {e.api_error_message()}")
            return []

    # ── INSIGHTS ─────────────────────────────────────────────────────────────
    def get_campaign_insights(
        self,
        date_preset: str = "yesterday",
        date_range: dict = None,
        objective_filter: str = None,
    ) -> list:
        """
        Lấy insights ở Campaign level (dùng cho CBO campaigns).
        SKILL.md rule: CBO → evaluate at Campaign level.
        """
        params = self._build_insight_params(
            level="campaign",
            date_preset=date_preset,
            date_range=date_range,
            fields=MESSENGER_ADS_FIELDS + ["buying_type", "bid_strategy"],
        )

        return self._fetch_insights(params, level="campaign", objective_filter=objective_filter)

    def get_adset_insights(
        self,
        campaign_id: str = None,
        date_preset: str = "yesterday",
        date_range: dict = None,
    ) -> list:
        """
        Lấy insights ở Ad Set level (dùng cho non-CBO).
        SKILL.md rule: non-CBO → evaluate at Ad Set level.
        """
        params = self._build_insight_params(
            level="adset",
            date_preset=date_preset,
            date_range=date_range,
            fields=MESSENGER_ADS_FIELDS,
        )
        if campaign_id:
            params["filtering"] = json.dumps([{
                "field": "campaign.id",
                "operator": "EQUAL",
                "value": campaign_id,
            }])

        return self._fetch_insights(params, level="adset")

    def get_ad_insights(
        self,
        adset_id: str = None,
        campaign_id: str = None,
        date_preset: str = "yesterday",
        date_range: dict = None,
    ) -> list:
        """Lấy insights ở Ad level."""
        params = self._build_insight_params(
            level="ad",
            date_preset=date_preset,
            date_range=date_range,
            fields=MESSENGER_ADS_FIELDS,
        )
        filters = []
        if campaign_id:
            filters.append({"field": "campaign.id", "operator": "EQUAL", "value": campaign_id})
        if adset_id:
            filters.append({"field": "adset.id", "operator": "EQUAL", "value": adset_id})
        if filters:
            params["filtering"] = json.dumps(filters)

        return self._fetch_insights(params, level="ad")

    # ── ACCOUNT LEVEL ────────────────────────────────────────────────────────
    def get_account_insights(self, date_preset: str = "yesterday") -> dict:
        """Lấy tổng quan account level (không drill-down campaign cụ thể)."""
        params = self._build_insight_params(
            level="account",
            date_preset=date_preset,
            date_range=None,
            fields=["impressions", "reach", "clicks", "inline_link_clicks",
                    "spend", "cpm", "cpc", "ctr", "actions", "cost_per_action_type",
                    "date_start", "date_stop"],
        )
        try:
            insights = self.account.get_insights(params=params)
            data = list(insights)
            if data:
                return self._process_insight_row(data[0], level="account")
            return {}
        except FacebookRequestError as e:
            print(f"❌ Lỗi get_account_insights: {e.api_error_message()}")
            return {}

    # ── INTERNAL HELPERS ─────────────────────────────────────────────────────
    def _build_insight_params(
        self,
        level: str,
        date_preset: str,
        date_range: dict,
        fields: list,
    ) -> dict:
        params = {
            "level": level,
            "fields": ",".join(fields),
        }
        if date_range:
            params["time_range"] = json.dumps(date_range)
        else:
            params["date_preset"] = date_preset
        return params

    def _fetch_insights(self, params: dict, level: str, objective_filter: str = None) -> list:
        """Fetch insights và process từng row."""
        try:
            insights = self.account.get_insights(params=params)
            results = []
            for row in insights:
                processed = self._process_insight_row(row, level)
                if objective_filter:
                    obj = processed.get("objective", "").upper()
                    if objective_filter.upper() not in obj:
                        continue
                results.append(processed)
            return results
        except FacebookRequestError as e:
            print(f"❌ Lỗi get insights level={level}: {e.api_error_message()}")
            return []

    def _process_insight_row(self, row, level: str) -> dict:
        """Normalize một row insight: extract actions, format numbers."""
        actions = row.get("actions", []) or []
        cost_per_action = row.get("cost_per_action_type", []) or []

        # Extract MCS (Messaging Conversations Started)
        mcs_value = _parse_actions(actions, "onsite_conversion.messaging_conversation_started_7d")
        cost_per_mcs = _parse_cost_per_action(cost_per_action, "onsite_conversion.messaging_conversation_started_7d")

        # Extract Engagement actions
        post_engagement = _parse_actions(actions, "post_engagement")
        post_reaction = _parse_actions(actions, "post_reaction")
        comment = _parse_actions(actions, "comment")
        share = _parse_actions(actions, "post")

        spend = _safe_float(row.get("spend"))
        impressions = _safe_float(row.get("impressions"))
        reach = _safe_float(row.get("reach"))
        frequency = (impressions / reach) if (impressions and reach and reach > 0) else None

        processed = {
            "level": level,
            "campaign_id": row.get("campaign_id"),
            "campaign_name": row.get("campaign_name"),
            "adset_id": row.get("adset_id"),
            "adset_name": row.get("adset_name"),
            "ad_id": row.get("ad_id"),
            "ad_name": row.get("ad_name"),
            "objective": row.get("objective"),
            "date_start": row.get("date_start"),
            "date_stop": row.get("date_stop"),
            # Core metrics
            "impressions": impressions,
            "reach": reach,
            "frequency": frequency,
            "clicks_all": _safe_float(row.get("clicks")),
            "link_clicks": _safe_float(row.get("inline_link_clicks")),
            "spend": spend,
            "currency": self.currency,
            "cpm": _safe_float(row.get("cpm")),
            "cpc_all": _safe_float(row.get("cpc")),
            "ctr_all": _safe_float(row.get("ctr")),
            "ctr_link": _safe_float(row.get("inline_link_click_ctr")),
            "cost_per_link_click": _safe_float(row.get("cost_per_inline_link_click")),
            # Messenger metrics
            "mcs": mcs_value,
            "cost_per_mcs": cost_per_mcs,
            # Engagement metrics
            "post_engagement": post_engagement,
            "post_reaction": post_reaction,
            "comment": comment,
            "share": share,
            # Calculated
            "cpe": (spend / post_engagement) if (spend and post_engagement and post_engagement > 0) else None,
            # Relevance rankings
            "quality_ranking": row.get("quality_ranking"),
            "conversion_rate_ranking": row.get("conversion_rate_ranking"),
            "engagement_rate_ranking": row.get("engagement_rate_ranking"),
            # Raw for debugging
            "_actions_raw": actions,
        }
        return processed

    # ── MUTATION ACTIONS (Requires ads_management) ───────────────────────────
    def update_campaign_status(self, campaign_id: str, status: str) -> bool:
        """
        Cập nhật trạng thái campaign. status: 'ACTIVE' hoặc 'PAUSED'.
        Yêu cầu token có quyền ads_management.
        """
        try:
            campaign = Campaign(campaign_id)
            campaign.api_update(params={"status": status.upper()})
            print(f"✅ Đã chuyển campaign {campaign_id} sang trạng thái {status.upper()}")
            return True
        except FacebookRequestError as e:
            print(f"❌ Lỗi update campaign {campaign_id}: {e.api_error_message()}")
            return False

    def update_adset_status(self, adset_id: str, status: str) -> bool:
        """Cập nhật trạng thái adset."""
        try:
            adset = AdSet(adset_id)
            adset.api_update(params={"status": status.upper()})
            print(f"✅ Đã chuyển adset {adset_id} sang trạng thái {status.upper()}")
            return True
        except FacebookRequestError as e:
            print(f"❌ Lỗi update adset {adset_id}: {e.api_error_message()}")
            return False

    def adjust_campaign_budget(self, campaign_id: str, new_budget_int: int) -> bool:
        """Điều chỉnh ngân sách hàng ngày của CBO campaign."""
        try:
            campaign = Campaign(campaign_id)
            campaign.api_update(params={"daily_budget": int(new_budget_int)})
            print(f"✅ Đã cập nhật ngân sách daily_budget cho {campaign_id} thành {new_budget_int}")
            return True
        except FacebookRequestError as e:
            print(f"❌ Lỗi chỉnh ngân sách campaign {campaign_id}: {e.api_error_message()}")
            return False
