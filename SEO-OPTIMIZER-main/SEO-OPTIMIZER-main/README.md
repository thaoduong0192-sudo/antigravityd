# SEO Analyzer Skill for Google Antigravity 🚀

[![Antigravity](https://img.shields.io/badge/Antigravity-Skill-blue)](https://antigravity.google)
[![Version](https://img.shields.io/badge/version-1.1.0-orange)](https://github.com/skylinedg/seo-analyzer-antigravity)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**SEO Analyzer** is a powerful skill for the Google Antigravity agent that performs deep SEO audits, generates a weighted score (0-100), and provides actionable fixes for your web pages.

---

## 🇺🇸 English Instructions

### 🎯 Key Features
- **Comprehensive Scoring**: Analyzes 5 key categories: Technical, On-Page, Content Quality, Core Web Vitals, and Links/Media.
- **Performance Insights**: Integrates with Google PageSpeed Insights for real-world performance data.
- **Automated Fixes**: Can automatically apply recommended fixes to local HTML files.
- **Prioritized Reporting**: Categorizes issues into Critical, Improvements, and Quick Wins.
- **Multi-language Support**: Detects your language and provides reports in English or Portuguese.

### 🚀 Installation

**Option 1 — Via Antigravity (Recommended):**
Simply ask the agent:
```bash
 Pull the seo-analyzer skill from GitHub: https://github.com/skylinedg/seo-analyzer-antigravity
```

**Option 2 — Manual Clone:**
```bash
git clone https://github.com/skylinedg/seo-analyzer-antigravity ~/.agents/skills/seo-analyzer
```

### 📖 Usage Examples

- "Analyze the SEO of https://example.com"
- "Do a full audit of my local index.html and apply critical fixes"
- "Check the SEO score of my landing page"

**Sample Output:**
```text
=======================================================
  SEO SCORE: 82/100  🟢
  Page: https://example.com
=======================================================

🟡 IMPROVEMENTS (Medium impact)
  [On-Page] -7 pts  →  Meta description: 95 chars (ideal: 120–158).

✅ ALREADY CORRECT
  • Title between 50–60 chars with keyword
  • Exactly 1 H1 tag
  • HTTPS active
```

---

## 🇧🇷 Instruções em Português

### 🎯 Funcionalidades Principais
- **Pontuação Completa**: Analisa 5 categorias: Técnico, On-Page, Qualidade de Conteúdo, Core Web Vitals e Links/Mídia.
- **Performance Real**: Integração opcional com Google PageSpeed Insights.
- **Correções Automáticas**: Capaz de aplicar correções diretamente em arquivos HTML locais.
- **Relatórios Priorizados**: Divide os problemas em Críticos, Melhorias e Ganhos Rápidos (Quick Wins).
- **Suporte Bilíngue**: Detecta seu idioma e gera relatórios em Inglês ou Português.

### 🚀 Instalação

**Opção 1 — Via Antigravity (Recomendado):**
Peça ao agente:
```bash
Puxe a skill seo-analyzer do GitHub: https://github.com/skylinedg/seo-analyzer-antigravity
```

**Opção 2 — Clone Manual:**
```bash
git clone https://github.com/skylinedg/seo-analyzer-antigravity ~/.agents/skills/seo-analyzer
```

### 📖 Exemplos de Uso

- "Analisa o SEO de https://meusite.com.br"
- "Faz um audit completo do meu index.html local e aplica os fixes críticos"
- "Qual o score de SEO da minha landing page?"

---

## 📁 Project Structure
```text
seo-analyzer/
├── SKILL.md        # Agent instructions & logic
├── scripts/        # Python tools (audit, vitals, report)
│   ├── seo_audit.py
│   ├── core_web_vitals.py
│   └── generate_report.py
└── references/     # SEO Rubrics & Best Practices
```

## 🤝 Contributing
Forks and Pull Requests are welcome! Support for more languages and new SEO checks is always appreciated.

---
*Made with ❤️ for the Antigravity Community.*
