#!/usr/bin/env python3
"""
core_web_vitals.py — Fetches Core Web Vitals via PageSpeed Insights API.
Usage: python core_web_vitals.py "<url>" [API_KEY]
Output: JSON to stdout
"""
import sys, json, urllib.request, urllib.parse

def fetch_vitals(url: str, api_key: str = "") -> dict:
    base = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    results = {}
    for strategy in ("mobile", "desktop"):
        params = {"url": url, "strategy": strategy, "category": "performance"}
        if api_key:
            params["key"] = api_key
        endpoint = f"{base}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(endpoint, timeout=30) as r:
            data = json.loads(r.read())
        cats   = data.get("lighthouseResult", {}).get("categories", {})
        audits = data.get("lighthouseResult", {}).get("audits", {})
        results[strategy] = {
            "performance_score": round((cats.get("performance", {}).get("score") or 0) * 100),
            "LCP_s":  audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000,
            "INP_ms": audits.get("interaction-to-next-paint", {}).get("numericValue", 0),
            "CLS":    audits.get("cumulative-layout-shift", {}).get("numericValue", 0),
            "FCP_s":  audits.get("first-contentful-paint", {}).get("numericValue", 0) / 1000,
            "TTFB_ms": audits.get("server-response-time", {}).get("numericValue", 0),
        }
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core_web_vitals.py <url> [api_key]"); sys.exit(1)
    url     = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else ""
    try:
        print(json.dumps(fetch_vitals(url, api_key), ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)})); sys.exit(1)
