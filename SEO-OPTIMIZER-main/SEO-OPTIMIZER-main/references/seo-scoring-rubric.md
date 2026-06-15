# SEO Scoring Rubric — seo-analyzer skill

## Deduction Table

### Technical SEO (max 25 pts)
| Check                          | Pass | Partial | Fail (deduct) |
|-------------------------------|------|---------|---------------|
| HTTPS enforced                | +5   | —       | -5            |
| robots.txt accessible         | +3   | —       | -3            |
| sitemap.xml valid             | +3   | malformed: -1 | -3        |
| Canonical tag present         | +4   | —       | -4            |
| No broken links (4xx/5xx)     | +5   | < 3 broken: -2 | -5     |
| Structured data valid JSON-LD | +5   | warnings: -2 | -5        |

### On-Page Elements (max 25 pts)
| Check                          | Pass | Partial | Fail (deduct) |
|-------------------------------|------|---------|---------------|
| Title 50–60 chars + keyword   | +8   | length wrong: -3 | -8   |
| Meta description 120–158 chars| +7   | length wrong: -3 | -7   |
| Single H1 with main keyword   | +6   | H1 present but no kw: -2 | -6 |
| URL slug clean + short        | +4   | —       | -4            |

### Content Quality (max 20 pts)
| Check                          | Pass | Partial | Fail (deduct) |
|-------------------------------|------|---------|---------------|
| Word count ≥ 300 (non-thin)   | +6   | 150-299 words: -3 | -6  |
| Heading hierarchy logical     | +4   | —       | -4            |
| Readability (Flesch ≥ 50)     | +5   | 30-49: -2 | -5          |
| No keyword stuffing (< 5% density) | +5 | —    | -5            |

### Core Web Vitals (max 20 pts)
| Metric   | Good       | Needs Work  | Poor        |
|----------|------------|-------------|-------------|
| LCP      | +7 (≤2.5s) | +3 (≤4.0s)  | 0 (>4.0s)   |
| INP      | +7 (≤200ms)| +3 (≤500ms) | 0 (>500ms)  |
| CLS      | +6 (≤0.1)  | +3 (≤0.25)  | 0 (>0.25)   |

### Link & Media (max 10 pts)
| Check                          | Pass | Partial | Fail (deduct) |
|-------------------------------|------|---------|---------------|
| All images with alt text      | +5   | < 20% missing: -2 | -5  |
| Internal links ≥ 2            | +3   | —       | -3            |
| Open Graph tags present       | +2   | —       | -2            |
