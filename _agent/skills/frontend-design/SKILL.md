---
name: frontend-design
description: Hệ thống Thiết kế Giao diện UI/UX Toàn diện & Quy trình AI-Native Design-to-Production (Anthropic SDLC, DesignMD tokens, Business Flows, UI/UX Pro Max 50+ styles/97 palettes, Claude Design prompting, và Kiểm định Pixel-Perfect tự động bằng Playwright / Chrome DevTools MCP). Kích hoạt khi thiết kế giao diện web/mobile, trích xuất Design System (DESIGN.md), chuyển bản vẽ Figma/HTML/zip sang code, hoặc kiểm toán chất lượng UI/UX.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Frontend Design System & AI-Native Design Master

> **Philosophy:** Every pixel has purpose. Restraint is luxury. User psychology drives decisions.
> **Core Principle:** THINK, don't memorize. ASK, don't assume. VERIFY via Visual & DOM Diff before shipping.

---

## 🎯 Selective Reading Rule (MANDATORY)

**Read REQUIRED files always, OPTIONAL only when needed:**

| File | Status | When to Read |
|------|--------|--------------|
| [ux-psychology.md](ux-psychology.md) | 🔴 **REQUIRED** | Always read first! |
| [ai-native-design-workflow.md](ai-native-design-workflow.md) | 🔴 **REQUIRED** | AI-Native SDLC 6-Stage Loop, `DESIGN.md`, `business-flows.md`, 5-Constraint Prompt & MCP Verification Gate |
| [color-system.md](color-system.md) | ⚪ Optional | Color/palette decisions |
| [typography-system.md](typography-system.md) | ⚪ Optional | Font selection/pairing |
| [visual-effects.md](visual-effects.md) | ⚪ Optional | Glassmorphism, shadows, gradients |
| [animation-guide.md](animation-guide.md) | ⚪ Optional | Animation needed |
| [motion-graphics.md](motion-graphics.md) | ⚪ Optional | Lottie, GSAP, 3D |
| [decision-trees.md](decision-trees.md) | ⚪ Optional | Context templates |

> 🔴 **`ux-psychology.md` + `ai-native-design-workflow.md` = ALWAYS READ. Others = only if relevant.**

---

## 🔧 Runtime Scripts & Design Intelligence Engine

**Execute these for design system generation, UX audits, and pixel-perfect DOM verification:**

| Script | Purpose | Usage |
|--------|---------|-------|
| `../../.shared/ui-ux-pro-max/scripts/search.py` | Generate full `DESIGN.md` / `MASTER.md` from 50+ styles, 97 palettes, 57 font pairings | `python d:/Antigravity/_agent/.shared/ui-ux-pro-max/scripts/search.py "<product> <industry> <keywords>" --design-system --persist -p "Project Name"` |
| `scripts/ux_audit.py` | UX Psychology & Accessibility Static Audit | `python d:/Antigravity/_agent/skills/frontend-design/scripts/ux_audit.py <project_path>` |
| `scripts/accessibility_checker.py` | WCAG Contrast & Semantic HTML Checker | `python d:/Antigravity/_agent/skills/frontend-design/scripts/accessibility_checker.py <project_path>` |
| `scripts/dom_diff_audit.js` | Live DOM BoundingRect & ComputedStyle Diff across 4 Viewports (`375px`, `768px`, `1024px`, `1440px`) via Chrome/Playwright MCP | Inject via `chrome_evaluate_js` or Playwright during Stage 4/5 QA |

---

## ⚠️ CRITICAL: ASK BEFORE ASSUMING (MANDATORY)

> **STOP! If the user's request is open-ended, DO NOT default to your favorites.**

### When User Prompt is Vague, ASK:

**Color not specified?** Ask:
> "What color palette do you prefer? (blue/green/orange/neutral/other?)"

**Style not specified?** Ask: 
> "What style are you going for? (minimal/bold/retro/futuristic/organic?)"

**Layout not specified?** Ask:
> "Do you have a layout preference? (single column/grid/asymmetric/full-width?)"

### ⛔ DEFAULT TENDENCIES TO AVOID (ANTI-SAFE HARBOR):

| AI Default Tendency | Why It's Bad | Think Instead |
|---------------------|--------------|---------------|
| **Bento Grids (Modern Cliché)** | Used in every AI design | Why does this content NEED a grid? |
| **Hero Split (Left/Right)** | Predictable & Boring | How about Massive Typography or Vertical Narrative? |
| **Mesh/Aurora Gradients** | The "new" lazy background | What's a radical color pairing? |
| **Glassmorphism** | AI's idea of "premium" | How about solid, high-contrast flat? |
| **Deep Cyan / Fintech Blue** | Safe harbor from purple ban | Why not Red, Black, or Neon Green? |
| **"Orchestrate / Empower"** | AI-generated copywriting | How would a human say this? |
| Dark background + neon glow | Overused, "AI look" | What does the BRAND actually need? |
| **Rounded everything** | Generic/Safe | Where can I use sharp, brutalist edges? |

> 🔴 **"Every 'safe' structure you choose brings you one step closer to a generic template. TAKE RISKS."**

---

## 1. Constraint Analysis (ALWAYS FIRST)

Before any design work, ANSWER THESE or ASK USER:

| Constraint | Question | Why It Matters |
|------------|----------|----------------|
| **Timeline** | How much time? | Determines complexity |
| **Content** | Ready or placeholder? | Affects layout flexibility |
| **Brand** | Existing guidelines? | May dictate colors/fonts |
| **Tech** | What stack? | Affects capabilities |
| **Audience** | Who exactly? | Drives all visual decisions |

### Audience → Design Approach

| Audience | Think About |
|----------|-------------|
| **Gen Z** | Bold, fast, mobile-first, authentic |
| **Millennials** | Clean, minimal, value-driven |
| **Gen X** | Familiar, trustworthy, clear |
| **Boomers** | Readable, high contrast, simple |
| **B2B** | Professional, data-focused, trust |
| **Luxury** | Restrained elegance, whitespace |

---

## 2. UX Psychology Principles

### Core Laws (Internalize These)

| Law | Principle | Application |
|-----|-----------|-------------|
| **Hick's Law** | More choices = slower decisions | Limit options, use progressive disclosure |
| **Fitts' Law** | Bigger + closer = easier to click | Size CTAs appropriately |
| **Miller's Law** | ~7 items in working memory | Chunk content into groups |
| **Von Restorff** | Different = memorable | Make CTAs visually distinct |
| **Serial Position** | First/last remembered most | Key info at start/end |

### Emotional Design Levels

```
VISCERAL (instant)  → First impression: colors, imagery, overall feel
BEHAVIORAL (use)    → Using it: speed, feedback, efficiency
REFLECTIVE (memory) → After: "I like what this says about me"
```

### Trust Building

- Security indicators on sensitive actions
- Social proof where relevant
- Clear contact/support access
- Consistent, professional design
- Transparent policies

---

## 3. Layout Principles

### Golden Ratio (φ = 1.618)

```
Use for proportional harmony:
├── Content : Sidebar = roughly 62% : 38%
├── Each heading size = previous × 1.618 (for dramatic scale)
├── Spacing can follow: sm → md → lg (each × 1.618)
```

### 8-Point Grid Concept

```
All spacing and sizing in multiples of 8:
├── Tight: 4px (half-step for micro)
├── Small: 8px
├── Medium: 16px
├── Large: 24px, 32px
├── XL: 48px, 64px, 80px
└── Adjust based on content density
```

### Key Sizing Principles

| Element | Consideration |
|---------|---------------|
| **Touch targets** | Minimum comfortable tap size |
| **Buttons** | Height based on importance hierarchy |
| **Inputs** | Match button height for alignment |
| **Cards** | Consistent padding, breathable |
| **Reading width** | 45-75 characters optimal |

---

## 4. Color Principles

### 60-30-10 Rule

```
60% → Primary/Background (calm, neutral base)
30% → Secondary (supporting areas)
10% → Accent (CTAs, highlights, attention)
```

### Color Psychology (For Decision Making)

| If You Need... | Consider Hues | Avoid |
|----------------|---------------|-------|
| Trust, calm | Blue family | Aggressive reds |
| Growth, nature | Green family | Industrial grays |
| Energy, urgency | Orange, red | Passive blues |
| Luxury, creativity | Deep Teal, Gold, Emerald | Cheap-feeling brights |
| Clean, minimal | Neutrals | Overwhelming color |

### Selection Process

1. **What's the industry?** (narrows options)
2. **What's the emotion?** (picks primary)
3. **Light or dark mode?** (sets foundation)
4. **ASK USER** if not specified

For detailed color theory: [color-system.md](color-system.md)

---

## 5. Typography Principles

### Scale Selection

| Content Type | Scale Ratio | Feel |
|--------------|-------------|------|
| Dense UI | 1.125-1.2 | Compact, efficient |
| General web | 1.25 | Balanced (most common) |
| Editorial | 1.333 | Readable, spacious |
| Hero/display | 1.5-1.618 | Dramatic impact |

### Pairing Concept

```
Contrast + Harmony:
├── DIFFERENT enough for hierarchy
├── SIMILAR enough for cohesion
└── Usually: display + neutral, or serif + sans
```

### Readability Rules

- **Line length**: 45-75 characters optimal
- **Line height**: 1.4-1.6 for body text
- **Contrast**: Check WCAG requirements
- **Size**: 16px+ for body on web

For detailed typography: [typography-system.md](typography-system.md)

---

## 6. Visual Effects Principles

### Glassmorphism (When Appropriate)

```
Key properties:
├── Semi-transparent background
├── Backdrop blur
├── Subtle border for definition
└── ⚠️ **WARNING:** Standard blue/white glassmorphism is a modern cliché. Use it radically or not at all.
```

### Shadow Hierarchy

```
Elevation concept:
├── Higher elements = larger shadows
├── Y-offset > X-offset (light from above)
├── Multiple layers = more realistic
└── Dark mode: may need glow instead
```

### Gradient Usage

```
Harmonious gradients:
├── Adjacent colors on wheel (analogous)
├── OR same hue, different lightness
├── Avoid harsh complementary pairs
├── 🚫 **NO Mesh/Aurora Gradients** (floating blobs)
└── VARY from project to project radically
```

For complete effects guide: [visual-effects.md](visual-effects.md)

---

## 7. Animation Principles

### Timing Concept

```
Duration based on:
├── Distance (further = longer)
├── Size (larger = slower)
├── Importance (critical = clear)
└── Context (urgent = fast, luxury = slow)
```

### Easing Selection

| Action | Easing | Why |
|--------|--------|-----|
| Entering | Ease-out | Decelerate, settle in |
| Leaving | Ease-in | Accelerate, exit |
| Emphasis | Ease-in-out | Smooth, deliberate |
| Playful | Bounce | Fun, energetic |

### Performance

- Animate only transform and opacity
- Respect reduced-motion preference
- Test on low-end devices

For animation patterns: [animation-guide.md](animation-guide.md), for advanced: [motion-graphics.md](motion-graphics.md)

---

## 8. "Wow Factor" Checklist

### Premium Indicators

- [ ] Generous whitespace (luxury = breathing room)
- [ ] Subtle depth and dimension
- [ ] Smooth, purposeful animations
- [ ] Attention to detail (alignment, consistency)
- [ ] Cohesive visual rhythm
- [ ] Custom elements (not all defaults)

### Trust Builders

- [ ] Security cues where appropriate
- [ ] Social proof / testimonials
- [ ] Clear value proposition
- [ ] Professional imagery
- [ ] Consistent design language

### Emotional Triggers

- [ ] Hero that evokes intended emotion
- [ ] Human elements (faces, stories)
- [ ] Progress/achievement indicators
- [ ] Moments of delight

---

## 9. Anti-Patterns (What NOT to Do)

### ❌ Lazy Design Indicators

- Default system fonts without consideration
- Stock imagery that doesn't match
- Inconsistent spacing
- Too many competing colors
- Walls of text without hierarchy
- Inaccessible contrast

### ❌ AI Tendency Patterns (AVOID!)

- **Same colors every project**
- **Dark + neon as default**
- **Purple/violet everything (PURPLE BAN ✅)**
- **Bento grids for simple landing pages**
- **Mesh Gradients & Glow Effects**
- **Same layout structure / Vercel clone**
- **Not asking user preferences**

### ❌ Dark Patterns (Unethical)

- Hidden costs
- Fake urgency
- Forced actions
- Deceptive UI
- Confirmshaming

---

## 10. Decision Process Summary

```
For EVERY design task:

1. CONSTRAINTS
   └── What's the timeline, brand, tech, audience?
   └── If unclear → ASK

2. CONTENT
   └── What content exists?
   └── What's the hierarchy?

3. STYLE DIRECTION
   └── What's appropriate for context?
   └── If unclear → ASK (don't default!)

4. EXECUTION
   └── Apply principles above
   └── Check against anti-patterns

5. REVIEW
   └── "Does this serve the user?"
   └── "Is this different from my defaults?"
   └── "Would I be proud of this?"
```

---

## Reference Files

For deeper guidance on specific areas:

- [ai-native-design-workflow.md](ai-native-design-workflow.md) - **AI-Native SDLC 6-Stage Loop, `DESIGN.md` extraction (`designmd.me`), `docs/01..06` & `business-flows.md` convention, 5-Constraint UI Prompting, and Playwright / Chrome DevTools MCP Verification Gate**
- [color-system.md](color-system.md) - Color theory and selection process
- [typography-system.md](typography-system.md) - Font pairing and scale decisions
- [visual-effects.md](visual-effects.md) - Effects principles and techniques
- [animation-guide.md](animation-guide.md) - Motion design principles
- [motion-graphics.md](motion-graphics.md) - Advanced: Lottie, GSAP, SVG, 3D, Particles
- [decision-trees.md](decision-trees.md) - Context-specific templates
- [ux-psychology.md](ux-psychology.md) - User psychology deep dive

---

## 11. AI-Native Design-to-Production Workflow (6-Step Master Loop)

To eliminate generic "AI-looking" UIs and ensure 100% consistency when building from scratch or adding new modules to an existing system, follow the **6-Step Design Master Workflow** (detailed in [ai-native-design-workflow.md](ai-native-design-workflow.md)):

### Step 1: Extract or Generate `DESIGN.md` & Trace `business-flows.md` (`01. INPUT`)
- **Existing Website / Reference Brand**: Extract exact design tokens (`DESIGN.md` + live HTML preview + Figma tokens) via **[designmd.me](https://designmd.me)** or inspect computed styles from the existing app into `docs/06-design/DESIGN.md`.
- **Greenfield Project**: Generate a tailored design system via `ui-ux-pro-max`:
  ```bash
  python d:/Antigravity/_agent/.shared/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system --persist -p "Project Name"
  ```
- **Numbered Project Documentation (`docs/01..06`)**:
  - `docs/01-tong-quan/intent.md` (Pain points & user intent)
  - `docs/02-ky-thuat/architecture.md` & `business-flows.md` (Numbered flows `QT-01`, `QT-02`... traced from backend/frontend source with Mermaid diagrams)
  - `docs/03-san-pham/spec.md` (Unified requirements + design spec)
  - `docs/06-design/DESIGN.md` & `<feature>-design.zip` (Reference HTML/CSS/Figma design package)

### Step 2: Structured 5-Constraint UI Design Prompting (`02. LOCAL DEVELOPMENT`)
When generating UI prototypes (in Claude Design Opus, Figma, or code), enforce all **5 Golden Constraints**:
1. **Responsive**: Desktop (`1440px`, `1024px`) & Mobile/Tablet (`768px`, `375px`) with zero horizontal overflow.
2. **Layout (Bố cục)**: Strict adherence to component hierarchy, 8-point spacing grid, and visual proportions in `DESIGN.md`.
3. **Colors (Màu sắc)**: Exact hex/CSS variable tokens from `DESIGN.md` across both Light Mode and Dark Mode.
4. **Components**: Modular, reusable, single-responsibility component breakdown.
5. **States & Micro-interactions (Trạng thái & Tương tác)**: Complete `hover`, `focus-visible`, `active`, `disabled`, `loading (skeleton)`, `empty`, and `error` states + smooth 150-250ms transitions for menus, modals, tabs, and forms.

### Step 3: Automated Pixel-Perfect Verification via Playwright / Chrome DevTools MCP (`04. DEV` & `05. QA`)
When implementing UI from `@docs/06-design/<feature>-design.zip` (or reference HTML/Figma) into `@<frontend-dir>`, ALWAYS run the **4-Point MCP Verification Gate** before declaring completion:
1. **Dual Server Mount**: Run the live frontend dev server (`localhost`) alongside the reference design HTML.
2. **Visual Screenshot Diff**: Capture and compare screenshots across all pages/tabs in both **Light Mode** and **Dark Mode** via Playwright / Chrome DevTools MCP (`chrome_screenshot`).
3. **DOM Coordinate & BoundingRect Diff Across 4 Viewports**: Inject [`scripts/dom_diff_audit.js`](scripts/dom_diff_audit.js) via `chrome_evaluate_js` / Playwright at **`375px`, `768px`, `1024px`, and `1440px`** to diff `{ tag, text, x, y, width, height, color, bg, border, font }` and fix any layout shift.
4. **Proactive Source Bug Fix & Clean Production Build**: Identify and fix subtle CSS/HTML bugs in the original mockup (e.g., stray quotes breaking `border`), document intentional improvements, and verify a zero-error `npm run build`.

---

## Related Skills

| Skill | When to Use |
|-------|-------------|
| **frontend-design** (this) | End-to-end UI/UX design thinking, `DESIGN.md` extraction, 6-step AI-Native Design-to-Production, and MCP Visual/DOM verification |
| **[web-design-guidelines](../web-design-guidelines/SKILL.md)** | After coding - Audit for accessibility, performance, and best practices |
| **[mobile-design](../mobile-design/SKILL.md)** | Touch psychology, iOS/Android platform guidelines, mobile navigation |
| **[tailwind-patterns](../tailwind-patterns/SKILL.md)** | Modern Tailwind CSS v4 architecture and responsive patterns |

## Post-Design Workflow

After implementing your design, run the complete audit loop:

```
1. INPUT & SPEC → Read DESIGN.md + business-flows.md (or generate via designmd.me / ui-ux-pro-max)
2. DESIGN       → Apply frontend-design principles & 5-Constraint Prompt
3. CODE         → Implement modular components in target frontend directory
4. MCP VERIFY   → Run Visual Screenshot Diff + DOM BoundingRect Diff (375/768/1024/1440px)
5. AUDIT & FIX  → Run ux_audit.py + web-design-guidelines + clean production build
```

> **Next Step:** After coding, run the MCP Visual/DOM Diff Gate and `web-design-guidelines` skill to verify pixel-perfect accuracy, accessibility, focus states, animations, and build health.

---

> **Remember:** Design is THINKING, not copying. Every project deserves fresh consideration based on its unique context and users. **Avoid the Modern SaaS Safe Harbor!**

---

## 12. Next.js 16+ Modern Form Patterns

> [!IMPORTANT]
> For Next.js 16+ projects, use the native `next/form` component instead of standard HTML `<form>` for all GET-based search/filter operations.

### The `<Form>` Component Advantage
- **Automatic Client Navigation:** Performs client-side transitions on submit.
- **Progressive Enhancement:** Works even without JavaScript.
- **URL Sync:** Automatically encodes input values into search params.

### Implementation Example (Search Bar)
```tsx
import Form from 'next/form'

export default function SearchBar() {
  return (
    <Form action="/search" className="flex gap-2">
      <input 
        name="q" 
        placeholder="Search products..." 
        className="border p-2"
      />
      <button type="submit">Search</button>
    </Form>
  )
}
```

### When to use `<Form>` vs. standard `<form>`:
- **Use `next/form`** for: Search, Filtering, Sorting, Pagination (GET requests).
- **Use standard `<form>`** for: Mutations, Login, Data Entry (POST requests via Server Actions).
