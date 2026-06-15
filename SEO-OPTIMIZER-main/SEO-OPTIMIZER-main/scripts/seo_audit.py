#!/usr/bin/env python3
"""
seo_audit.py — Audits technical and on-page metadata.
Usage: python seo_audit.py "<url_or_path>"
Output: JSON to stdout
"""
import sys, json, re, urllib.request, urllib.error
from html.parser import HTMLParser
from pathlib import Path

def fetch_content(target: str) -> str:
    if target.startswith("http"):
        req = urllib.request.Request(target, headers={"User-Agent": "SEO-Analyzer/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode("utf-8", errors="replace")
    return Path(target).read_text(encoding="utf-8")

class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = {
            "title": None, "meta_description": None, "canonical": None,
            "robots_meta": None, "h1_list": [], "h2_count": 0, "h3_count": 0,
            "images": [], "links": [], "og_tags": {}, "twitter_tags": {},
            "json_ld": [], "viewport": False, "h_stack": []
        }
        self._in_title = False; self._in_script = False; self._script_buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            n, c = a.get("name","").lower(), a.get("content","")
            p = a.get("property","").lower()
            if n == "description": self.data["meta_description"] = c
            if n == "robots":      self.data["robots_meta"] = c
            if n == "viewport":    self.data["viewport"] = True
            if p.startswith("og:"): self.data["og_tags"][p] = c
            if p.startswith("twitter:"): self.data["twitter_tags"][p] = c
        elif tag == "link" and a.get("rel","") == "canonical":
            self.data["canonical"] = a.get("href")
        elif tag == "h1": self.data["h_stack"].append("h1")
        elif tag == "h2": self.data["h2_count"] += 1
        elif tag == "h3": self.data["h3_count"] += 1
        elif tag == "img":
            self.data["images"].append({"src": a.get("src",""), "alt": a.get("alt")})
        elif tag == "a":
            self.data["links"].append(a.get("href",""))
        elif tag == "script" and a.get("type","") == "application/ld+json":
            self._in_script = True; self._script_buf = ""

    def handle_data(self, data):
        if self._in_title: self.data["title"] = (self.data["title"] or "") + data
        if self._in_script: self._script_buf += data

    def handle_endtag(self, tag):
        if tag == "title": self._in_title = False
        if tag == "h1" and self.data["h_stack"]:
            self.data["h1_list"].append(self.data["h_stack"].pop())
        if tag == "script" and self._in_script:
            self._in_script = False
            try: self.data["json_ld"].append(json.loads(self._script_buf))
            except json.JSONDecodeError: self.data["json_ld"].append("INVALID_JSON")

def audit(target: str) -> dict:
    html = fetch_content(target)
    parser = SEOParser(); parser.feed(html)
    d = parser.data

    title     = (d["title"] or "").strip()
    meta_desc = d["meta_description"] or ""
    images    = d["images"]
    links     = [l for l in d["links"] if l and not l.startswith("#")]

    missing_alt   = [i for i in images if i["alt"] is None]
    empty_alt     = [i for i in images if i["alt"] == ""]
    internal_links = [l for l in links if not l.startswith("http")]
    external_links = [l for l in links if l.startswith("http")]

    # Readability proxy — avg words per sentence
    text = re.sub(r"<[^>]+>", " ", html)
    words = re.findall(r"\b\w+\b", text)
    sentences = re.split(r"[.!?]+", text)
    avg_wps = round(len(words) / max(len(sentences), 1), 1)
    flesch_proxy = max(0, min(100, 206 - 1.015 * avg_wps))

    return {
        "target": target,
        "title": {"value": title, "length": len(title)},
        "meta_description": {"value": meta_desc, "length": len(meta_desc)},
        "canonical": d["canonical"],
        "robots_meta": d["robots_meta"],
        "viewport": d["viewport"],
        "h1_count": len(d["h1_list"]),
        "h2_count": d["h2_count"],
        "h3_count": d["h3_count"],
        "images_total": len(images),
        "images_missing_alt": len(missing_alt),
        "images_empty_alt": len(empty_alt),
        "internal_links": len(internal_links),
        "external_links": len(external_links),
        "og_tags": d["og_tags"],
        "twitter_tags": d["twitter_tags"],
        "json_ld": d["json_ld"],
        "word_count": len(words),
        "flesch_readability_proxy": round(flesch_proxy),
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seo_audit.py <url_or_file>"); sys.exit(1)
    try:
        result = audit(sys.argv[1])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)})); sys.exit(1)
