# SEO Best Practices — Referência do Agente (2026)

> Este arquivo é consultado pelo agente durante a fase de geração de relatório
> (Phase 4) para enriquecer recomendações com contexto, thresholds atualizados
> e exemplos de código prontos para uso.

---

## 1. Title Tag

**Regra:** 50–60 caracteres, keyword principal no início, única por página. [web:23]

**Por quê:** Títulos truncados no SERP perdem cliques. Títulos duplicados
diluem autoridade de página.

**Padrão recomendado:**
```html
<title>Keyword Principal | Nome do Site</title>
<!-- ou -->
<title>Keyword Principal: Subtítulo Complementar</title>
```

**Anti-padrões:**
- Título genérico: `<title>Home</title>`
- Keyword stuffing: `<title>Seguro Seguro Barato Seguro Online Seguro Auto</title>`
- Acima de 60 chars: truncado no Google com "…"

---

## 2. Meta Description

**Regra:** 120–158 caracteres, incluir keyword + CTA implícito, única por página. [web:20]

**Por quê:** Não é fator de ranking direto, mas afeta CTR — que é sinal
indireto de relevância.

```html
<meta name="description" content="Descrição clara do que o usuário encontrará,
com a keyword natural e um motivo para clicar. Máx 158 chars.">
```

**Anti-padrões:**
- Meta description vazia (Google gera automaticamente, geralmente pior)
- Descrição idêntica em todas as páginas
- Acima de 158 chars: truncada no SERP

---

## 3. Hierarquia de Headings

**Regra:** Exatamente 1 `<h1>` por página; estrutura lógica H1 → H2 → H3. [web:22]

**Por quê:** O H1 sinaliza o tópico principal da página. Múltiplos H1s
confundem crawlers sobre o tema central.

```html
<h1>Keyword Principal da Página</h1>
  <h2>Subtópico A</h2>
    <h3>Detalhe do Subtópico A</h3>
  <h2>Subtópico B</h2>
```

**Anti-padrões:**
- Usar H2/H3 para estética sem hierarquia semântica
- Pular níveis (H1 → H3 sem H2)
- H1 com texto genérico como "Bem-vindo"

---

## 4. URL Slug

**Regra:** Curto (< 75 chars), hífen como separador, keyword incluída,
sem stop words, lowercase. [web:20]

```
✅ /seguros/seguro-auto-barato
❌ /paginas/p?id=1234&cat=seguros&tipo=auto
❌ /seguros/o-melhor-seguro-de-automovel-que-voce-pode-encontrar-online
```

---

## 5. Canonical Tag

**Regra:** Presente em toda página, apontando para a URL preferencial
(HTTPS, www ou non-www padronizado, sem parâmetros UTM). [web:28]

```html
<link rel="canonical" href="https://www.seusite.com.br/pagina/">
```

**Quando usar self-referencing canonical:** Em todas as páginas,
mesmo sem duplicatas — evita que parâmetros de URL criem versões duplicadas.

**Anti-padrões:**
- Canonical apontando para URL diferente da atual sem intenção clara
- Página em sitemap com canonical para outra URL (mixed signals)

---

## 6. HTTPS

**Regra:** 100% das páginas em HTTPS; redirecionar HTTP → HTTPS com 301. [web:17]

**Por quê:** Sinal de ranking confirmado pelo Google. HTTP exibe aviso
"Não seguro" nos navegadores, aumentando bounce rate.

**Verificações adicionais:**
- Certificado não expirado
- Mixed content (recursos HTTP carregados em página HTTPS) eliminado
- HSTS header configurado no servidor

---

## 7. Core Web Vitals

Métricas medidas no **mobile** (Google usa mobile-first indexing). [web:21][web:27]

| Métrica | Bom      | Precisa Melhorar | Ruim     |
|---------|----------|------------------|----------|
| LCP     | ≤ 2.5s   | ≤ 4.0s           | > 4.0s   |
| INP     | ≤ 200ms  | ≤ 500ms          | > 500ms  |
| CLS     | ≤ 0.1    | ≤ 0.25           | > 0.25   |

**Principais causas de LCP alto e fixes:**
```html
<!-- Imagem LCP: evitar lazy load, usar fetchpriority -->
<img src="hero.webp" alt="..." fetchpriority="high" loading="eager"
     width="1200" height="600">
```
- Usar CDN para recursos estáticos
- Ativar compressão Brotli/Gzip no servidor
- Eliminar render-blocking CSS/JS acima do fold

**Principais causas de CLS alto e fixes:**
```css
/* Reservar espaço para imagens e embeds */
img, video, iframe { aspect-ratio: attr(width) / attr(height); }
```
- Definir `width` e `height` em todas as imagens
- Evitar inserção de banners/anúncios acima do conteúdo após carregamento
- Carregar fontes com `font-display: swap`

**Principais causas de INP alto e fixes:**
- Quebrar tarefas JavaScript longas com `scheduler.yield()`
- Evitar event listeners síncronos pesados em cliques
- Usar `will-change: transform` com moderação em animações

---

## 8. Structured Data / JSON-LD

**Regra:** Implementar JSON-LD (não Microdata) para o tipo mais relevante
da página. Páginas com schema têm CTR 20–40% maior. [web:17][web:25]

**Tipos mais comuns:**

```json
// Artigo de blog
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Título do Artigo",
  "author": {"@type": "Person", "name": "Nome Autor"},
  "datePublished": "2026-03-01",
  "image": "https://seusite.com.br/imagem.jpg"
}
```

```json
// FAQ (aumenta espaço no SERP)
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "Qual a pergunta?",
    "acceptedAnswer": {"@type": "Answer", "text": "Resposta completa."}
  }]
}
```

```json
// Produto / E-commerce
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Nome do Produto",
  "offers": {"@type": "Offer", "price": "99.90", "priceCurrency": "BRL"},
  "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.8", "reviewCount": "120"}
}
```

**Validação:** https://search.google.com/test/rich-results

---

## 9. Open Graph & Twitter Cards

**Regra:** Presentes em todas as páginas para controlar aparência
em compartilhamentos sociais. [web:23]

```html
<!-- Open Graph (Facebook, LinkedIn, WhatsApp) -->
<meta property="og:title"       content="Título da Página">
<meta property="og:description" content="Descrição para compartilhamento.">
<meta property="og:image"       content="https://seusite.com.br/og-image.jpg">
<meta property="og:url"         content="https://seusite.com.br/pagina/">
<meta property="og:type"        content="website">

<!-- Twitter Card -->
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:title"       content="Título da Página">
<meta name="twitter:description" content="Descrição para Twitter.">
<meta name="twitter:image"       content="https://seusite.com.br/og-image.jpg">
```

**Tamanho da og:image recomendado:** 1200×630px, < 1MB.

---

## 10. Alt Text em Imagens

**Regra:** Todo `<img>` deve ter `alt` descritivo. Imagens decorativas
usam `alt=""` (não omitido). [web:20]

```html
<!-- ✅ Descritivo e contextual -->
<img src="grafico-ctr.png" alt="Gráfico de CTR médio por posição no Google SERP 2026">

<!-- ✅ Decorativa — alt vazio (correto) -->
<img src="divider.svg" alt="">

<!-- ❌ Genérico -->
<img src="img001.jpg" alt="imagem">

<!-- ❌ Keyword stuffing no alt -->
<img src="foto.jpg" alt="seguro auto seguro carro seguro barato seguro online">
```

---

## 11. Robots.txt e Sitemap

**Regra:** `robots.txt` na raiz, sem bloquear recursos CSS/JS necessários
para renderização; `sitemap.xml` submetido ao Google Search Console. [web:20][web:22]

```
# robots.txt mínimo recomendado
User-agent: *
Disallow: /admin/
Disallow: /wp-json/
Disallow: /*?s=          # bloqueia resultados de busca interna
Allow: /

Sitemap: https://www.seusite.com.br/sitemap.xml
```

**Anti-padrões:**
- `Disallow: /` em produção (bloqueia indexação total)
- Bloquear `/wp-content/` ou `/assets/` (impede renderização pelo Googlebot)
- Sitemap com URLs 404 ou canonicalizadas para outras páginas

---

## 12. Conteúdo e Legibilidade

**Regras gerais:** [web:20][web:26]
- Mínimo 300 palavras para evitar "thin content"
- Keyword principal nos primeiros 100 palavras do corpo
- Frases com média de até 20 palavras (Flesch ≥ 50)
- Parágrafos curtos (3–5 linhas)
- Atualizar conteúdo periodicamente (freshness é sinal de ranking)

**Densidade de keyword:** 1–3% do total de palavras. Acima de 5% é
considerado keyword stuffing e pode gerar penalidade manual.

**Search Intent — tipos e formatos esperados:**

| Intent       | Tipo de página ideal         |
|--------------|------------------------------|
| Informacional | Blog post, guia, FAQ         |
| Navegacional  | Homepage, página de marca    |
| Comercial     | Comparativo, review, lista   |
| Transacional  | Landing page, página produto |

---

## 13. Links Internos

**Regra:** Mínimo 2 links internos por página; usar anchor text descritivo
com keyword da página de destino. [web:26]

```html
<!-- ✅ Anchor text descritivo -->
<a href="/blog/seo-tecnico">Aprenda mais sobre SEO Técnico</a>

<!-- ❌ Anchor text genérico -->
<a href="/blog/seo-tecnico">clique aqui</a>
```

**Benefícios:** Distribui PageRank interno, melhora crawlability e
mantém usuário no site (reduz bounce rate).

---

## 14. Mobile-First

**Regra:** Meta viewport obrigatório; conteúdo idêntico entre versões
mobile e desktop (Google usa mobile-first indexing). [web:21]

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

**Verificação:** Google Search Console → Experiência → Usabilidade em dispositivos móveis.

---

## 15. Táticas Proibidas (Black Hat)

O agente NUNCA deve recomendar: [web:17]

- **Keyword stuffing** — repetição excessiva de termos para manipular ranking
- **Hidden text** — texto branco em fundo branco, `display:none` com conteúdo
- **Cloaking** — exibir conteúdo diferente para Googlebot e usuários
- **Link farms / PBNs** — redes de links artificiais
- **Doorway pages** — páginas criadas apenas para ranquear, sem valor ao usuário
- **Conteúdo duplicado intencional** — copiar conteúdo de outros sites sem canonical
