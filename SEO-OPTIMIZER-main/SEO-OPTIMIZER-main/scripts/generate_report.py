#!/usr/bin/env python3
"""
generate_report.py — Calculates SEO Score and prints prioritized report.
Supports English and Portuguese.
Usage: python generate_report.py '<json_audit>' ['<json_vitals>'] [--lang en|pt]
"""
import sys, json, argparse

STRINGS = {
    "en": {
        "title": "SEO Analyzer Report",
        "score_label": "SEO SCORE",
        "page_label": "Page",
        "critical": "🔴 CRITICAL (High impact on score)",
        "improvements": "🟡 IMPROVEMENTS (Medium impact)",
        "quick_wins": "⚡ QUICK WINS",
        "already_correct": "✅ ALREADY CORRECT",
        "pts": "pts",
        "ideal": "ideal",
        "chars": "chars",
        "adjustment": "Adjustment",
        "found": "Found",
        "tags": "tags",
        "add": "Add",
        "missing": "Missing",
        "images": "images",
        "no_alt": "without descriptive alt text",
        "example": "Example",
        "only": "Only",
        "internal_links": "internal links. Add links to related pages.",
        "content_words": "Content with only {count} words (min: 300). Expand with useful info.",
        "readability": "Estimated readability: {score}/100. Use shorter sentences (< 20 words) and accessible vocabulary.",
        "no_h2": "No H2 tags found. Structure content with H2 and H3 subheadings.",
        "https_msg": "Page served via HTTP. Migrate to HTTPS.",
        "canonical_msg": "Canonical tag missing. Add: `<link rel=\"canonical\" href=\"https://yoursite.com/page/\">`",
        "viewport_msg": "Meta viewport missing. Add: `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">`",
        "json_ld_msg": "JSON-LD missing or invalid. Add relevant structured data (Article, Product, FAQ, etc.).",
        "og_msg": "Open Graph missing. Add `<meta property=\"og:title\">`, `og:description`, `og:image`.",
        "title_rubric": "Title between 50–60 chars with keyword",
        "metadesc_rubric": "Meta description between 120–158 chars",
        "h1_rubric": "Exactly 1 H1 tag",
        "canonical_rubric": "Canonical tag present",
        "https_rubric": "HTTPS active",
        "viewport_rubric": "Meta viewport present",
        "json_ld_rubric": "Valid JSON-LD",
        "og_rubric": "Open Graph tags present",
        "alt_rubric": "All images with alt text",
        "internal_links_rubric": "≥ 2 internal links",
        "word_count_rubric": "Word count ≥ 300",
        "readability_rubric": "Flesch readability ≥ 50",
        "h_hierarchy_rubric": "Logical heading hierarchy (H1→H2→H3)",
        "h1_fix": "exactly 1",
    },
    "pt": {
        "title": "Relatório SEO Analyzer",
        "score_label": "SEO SCORE",
        "page_label": "Página",
        "critical": "🔴 CRÍTICO (alto impacto no score)",
        "improvements": "🟡 MELHORIAS (impacto médio)",
        "quick_wins": "⚡ QUICK WINS",
        "already_correct": "✅ JÁ CORRETO",
        "pts": "pts",
        "ideal": "ideal",
        "chars": "chars",
        "adjustment": "Ajuste",
        "found": "Encontrado(s)",
        "tags": "tag(s)",
        "add": "Adicione",
        "missing": "ausente",
        "images": "imagens",
        "no_alt": "sem alt text descritivo",
        "example": "Exemplo",
        "only": "Apenas",
        "internal_links": "links internos. Adicione links para páginas relacionadas.",
        "content_words": "Conteúdo com apenas {count} palavras (mínimo: 300). Expanda com informações úteis.",
        "readability": "Legibilidade estimada: {score}/100. Use frases mais curtas (< 20 palavras) e vocabulário acessível.",
        "no_h2": "Nenhuma tag H2 encontrada. Estruture o conteúdo com subtítulos H2 e H3.",
        "https_msg": "Página servida via HTTP. Migre para HTTPS.",
        "canonical_msg": 'Tag canonical ausente. Adicione: `<link rel="canonical" href="https://seusite.com/pagina/">`',
        "viewport_msg": 'Meta viewport ausente. Adicione: `<meta name="viewport" content="width=device-width, initial-scale=1">`',
        "json_ld_msg": "JSON-LD ausente ou inválido. Adicione structured data relevante (Article, Product, FAQ, etc.).",
        "og_msg": 'Open Graph ausente. Adicione `<meta property="og:title">`, `og:description`, `og:image`.',
        "title_rubric": "Title entre 50–60 chars com keyword",
        "metadesc_rubric": "Meta description entre 120–158 chars",
        "h1_rubric": "Exatamente 1 tag H1",
        "canonical_rubric": "Tag canonical presente",
        "https_rubric": "HTTPS ativo",
        "viewport_rubric": "Meta viewport presente",
        "json_ld_rubric": "JSON-LD válido",
        "og_rubric": "Open Graph tags presentes",
        "alt_rubric": "Todas imagens com alt text",
        "internal_links_rubric": "≥ 2 links internos",
        "word_count_rubric": "Contagem de palavras ≥ 300",
        "readability_rubric": "Legibilidade Flesch ≥ 50",
        "h_hierarchy_rubric": "Hierarquia de headings lógica (H1→H2→H3)",
        "h1_fix": "exatamente 1",
    }
}

def get_rubric(lang):
    s = STRINGS[lang]
    return {
        "title_ok":        ("On-Page",    8, s["title_rubric"]),
        "metadesc_ok":     ("On-Page",    7, s["metadesc_rubric"]),
        "h1_ok":           ("On-Page",    6, s["h1_rubric"]),
        "canonical_ok":    ("Technical",  4, s["canonical_rubric"]),
        "https_ok":        ("Technical",  5, s["https_rubric"]),
        "viewport_ok":     ("Technical",  3, s["viewport_rubric"]),
        "json_ld_ok":      ("Technical",  5, s["json_ld_rubric"]),
        "og_ok":           ("Links/Media",2, s["og_rubric"]),
        "alt_ok":          ("Links/Media",5, s["alt_rubric"]),
        "internal_links_ok":("Links/Media",3, s["internal_links_rubric"]),
        "word_count_ok":   ("Content",    6, s["word_count_rubric"]),
        "readability_ok":  ("Content",    5, s["readability_rubric"]),
        "h_hierarchy_ok":  ("Content",    4, s["h_hierarchy_rubric"]),
    }

def score_audit(a: dict, v: dict | None, lang: str) -> tuple[int, list, list, list, list]:
    checks, issues = {}, []
    s = STRINGS[lang]
    rubric = get_rubric(lang)

    tlen = a["title"]["length"]
    checks["title_ok"] = 50 <= tlen <= 60
    if not checks["title_ok"]:
        issues.append(("On-Page", 8, "title",
            f"Title: {tlen} {s['chars']} ({s['ideal']}: 50–60). "
            f"{s['adjustment']}: `<title>Keyword | Site Name</title>`"))

    dlen = a["meta_description"]["length"]
    checks["metadesc_ok"] = 120 <= dlen <= 158
    if not checks["metadesc_ok"]:
        issues.append(("On-Page", 7, "meta_description",
            f"Meta description: {dlen} {s['chars']} ({s['ideal']}: 120–158). "
            f"{s['adjustment']}: `<meta name=\"description\" content=\"Concise description with keyword, max 158 chars.\">`"))

    checks["h1_ok"] = a["h1_count"] == 1
    if not checks["h1_ok"]:
        issues.append(("On-Page", 6, "h1",
            f"{s['found']} {a['h1_count']} H1 {s['tags']} ({s['ideal']}: {s['h1_fix']}). "
            f"{s['add']} `<h1>Main Title with Keyword</h1>`."))

    checks["canonical_ok"] = bool(a["canonical"])
    if not checks["canonical_ok"]:
        issues.append(("Technical", 4, "canonical", s["canonical_msg"]))

    checks["https_ok"] = a["target"].startswith("https") or not a["target"].startswith("http")
    if not checks["https_ok"]:
        issues.append(("Technical", 5, "https", s["https_msg"]))

    checks["viewport_ok"] = a["viewport"]
    if not checks["viewport_ok"]:
        issues.append(("Technical", 3, "viewport", s["viewport_msg"]))

    checks["json_ld_ok"] = bool(a["json_ld"]) and "INVALID_JSON" not in a["json_ld"]
    if not checks["json_ld_ok"]:
        issues.append(("Technical", 5, "json_ld", s["json_ld_msg"]))

    checks["og_ok"] = bool(a["og_tags"])
    if not checks["og_ok"]:
        issues.append(("Links/Media", 2, "og", s["og_msg"]))

    missing = a["images_missing_alt"] + a["images_empty_alt"]
    checks["alt_ok"] = missing == 0
    if not checks["alt_ok"]:
        issues.append(("Links/Media", 5, "alt",
            f"{missing}/{a['images_total']} {s['images']} {s['no_alt']}. "
            f"{s['example']}: `<img src=\"...\" alt=\"Contextual description\">`"))

    checks["internal_links_ok"] = a["internal_links"] >= 2
    if not checks["internal_links_ok"]:
        issues.append(("Links/Media", 3, "internal_links",
            f"{s['only']} {a['internal_links']} {s['internal_links']}"))

    checks["word_count_ok"] = a["word_count"] >= 300
    if not checks["word_count_ok"]:
        issues.append(("Content", 6, "word_count",
            s["content_words"].format(count=a['word_count'])))

    checks["readability_ok"] = a["flesch_readability_proxy"] >= 50
    if not checks["readability_ok"]:
        issues.append(("Content", 5, "readability",
            s["readability"].format(score=a['flesch_readability_proxy'])))

    checks["h_hierarchy_ok"] = a["h2_count"] > 0
    if not checks["h_hierarchy_ok"]:
        issues.append(("Content", 4, "h_hierarchy", s["no_h2"]))

    # Base score
    score = sum(rubric[k][1] for k, v in checks.items() if v)

    # Core Web Vitals (max 20)
    cwv_score = 0
    if v:
        mob = v.get("mobile", {})
        lcp = mob.get("LCP_s", 99)
        inp = mob.get("INP_ms", 9999)
        cls = mob.get("CLS", 99)
        cwv_score += 7 if lcp <= 2.5 else (3 if lcp <= 4.0 else 0)
        cwv_score += 7 if inp <= 200 else (3 if inp <= 500 else 0)
        cwv_score += 6 if cls <= 0.1 else (3 if cls <= 0.25 else 0)
    score += cwv_score

    passing  = [k for k, ok in checks.items() if ok]
    critical = sorted([i for i in issues if i[1] >= 8], key=lambda x: -x[1])
    improve  = sorted([i for i in issues if 3 <= i[1] <= 7], key=lambda x: -x[1])
    quick    = sorted([i for i in issues if i[1] <= 2], key=lambda x: -x[1])
    return score, critical, improve, quick, passing

def traffic_light(s): return "🟢" if s >= 80 else ("🟡" if s >= 50 else "🔴")

def print_report(a, v=None, lang="en"):
    s = STRINGS[lang]
    rubric = get_rubric(lang)
    score, critical, improve, quick, passing = score_audit(a, v, lang)
    tl = traffic_light(score)
    print(f"\n{'='*55}")
    print(f"  {s['score_label']}: {score}/100  {tl}")
    print(f"  {s['page_label']}: {a['target']}")
    print(f"{'='*55}\n")
    if critical:
        print(f"{s['critical']}\n")
        for cat, pts, key, msg in critical:
            print(f"  [{cat}] -{pts} {s['pts']}  →  {msg}\n")
    if improve:
        print(f"{s['improvements']}\n")
        for cat, pts, key, msg in improve:
            print(f"  [{cat}] -{pts} {s['pts']}  →  {msg}\n")
    if quick:
        print(f"{s['quick_wins']}\n")
        for cat, pts, key, msg in quick:
            print(f"  [{cat}] -{pts} {s['pts']}  →  {msg}\n")
    if passing:
        print(f"{s['already_correct']}")
        for k in passing:
            print(f"  • {rubric[k][2]}")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SEO report.")
    parser.add_argument("audit_json", help="JSON data from seo_audit.py")
    parser.add_argument("vitals_json", nargs="?", default=None, help="JSON data from core_web_vitals.py")
    parser.add_argument("--lang", choices=["en", "pt"], default="en", help="Language of the report (en or pt)")
    
    args = parser.parse_args()
    
    audit_data = json.loads(args.audit_json)
    vitals_data = json.loads(args.vitals_json) if args.vitals_json else None
    
    print_report(audit_data, vitals_data, args.lang)

