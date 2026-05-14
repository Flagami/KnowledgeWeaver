# KnowledgeWeaver Frontend Redesign — Academic/Scholarly Editorial

**Date:** 2026-05-14
**Scope:** `knowledgeweaver/ui/web/index.html` (single file, no backend changes)

## Overview

Redesign the KnowledgeWeaver web UI from its current Apple-style aesthetic (light gray, blue accents, system sans-serif fonts) to an academic/scholarly editorial aesthetic inspired by premium journals like *Nature* and *The Atlantic*. The goal is a richer, more authoritative feel that matches the intellectual weight of the tool's purpose — AI-powered research synthesis.

## Design Direction

**Option A — The Journal.** Warm ivory base, deep ink-black type, Cormorant Garamond display font, EB Garamond body, warm gold accent. Feels like a premium academic publication: serious, beautiful, timeless.

## Color Palette

| Token | Value | Usage |
|---|---|---|
| `--bg` | `#faf8f4` | Page background — warm ivory |
| `--card` | `#fefcf8` | Card/surface background |
| `--text` | `#1a1209` | Primary text — deep warm black |
| `--muted` | `#6b5c3e` | Secondary text, labels, metadata |
| `--accent` | `#8b6914` | Interactive elements, links, active states |
| `--accent-light` | `rgba(139,105,20,0.08)` | Hover backgrounds, focus rings |
| `--border` | `rgba(139,105,20,0.12)` | Card and input borders |
| `--rule` | `#c9a84c` | Hairline decorative rules |
| `--header-bg` | `rgba(250,248,244,0.92)` | Frosted header background |

**What changes:** Apple blue (`#0071e3`) → warm gold (`#8b6914`) throughout. Apple gray (`#f5f5f7`) → warm ivory (`#faf8f4`).

## Typography

| Role | Font | Source |
|---|---|---|
| Display / headings | Cormorant Garamond | Google Fonts |
| Body / labels | EB Garamond | Google Fonts |
| Monospace (timestamps, badges) | Courier Prime | Google Fonts |
| Fallback | Georgia, serif | System |

All three fonts loaded via a single Google Fonts `<link>` in `<head>`. No local font dependency.

**What changes:** System sans-serif stack replaced entirely. Section labels become small-caps EB Garamond. Headings become Cormorant Garamond.

## Component Redesign

### Header
- Logo: "KnowledgeWeaver" in Cormorant Garamond italic — no icon, just the name in elegant type
- A single hairline gold rule (`#c9a84c`, 1px) runs the full width underneath the header
- Active processing indicator: small italic EB Garamond text ("2 researching…") instead of a pill badge
- Background: warm frosted glass (`rgba(250,248,244,0.92)` + backdrop-filter blur)

### Explore Card — Search Area
- Heading "What do you want to explore?" in Cormorant Garamond, ~1.8rem, italic weight
- Input field: rectangular with subtle warm border; on focus, bottom border only turns gold (no box-shadow ring)
- "Explore →" button: rectangular (not pill-shaped), outlined in gold, EB Garamond text, no fill — fills gold on hover
- "Suggested Topics" label: small-caps EB Garamond

### Bubble Cloud
- Keep the floating animation concept (CSS `bubbleFloat` keyframes)
- Shape: oval/pill (border-radius ~50px) instead of perfect circles
- Fill: `#fefcf8` (warm cream), border: `rgba(139,105,20,0.3)` (gold)
- Text: Cormorant Garamond, warm ink color
- Fewer, larger bubbles feel more editorial than many small ones
- Color schemes: warm tones only (cream, ivory, parchment) — no pastel rainbow

### Research Library
- Each query row: thin gold left border (`3px solid #c9a84c`) when status is `processing`
- Status badges: small-caps EB Garamond text, color-only differentiation — no colored background fills
  - pending: `var(--muted)`
  - processing: `var(--accent)` + italic
  - completed: `#2d6a2d` (warm forest green)
  - failed: `#8b2020` (warm deep red)
- Timestamps: Courier Prime
- Empty state: italic Cormorant Garamond — *"No research yet. Enter a topic above to begin."*
- "Open Report ↗" link: EB Garamond, gold color, no underline until hover

### Toast Notifications
- Background: `#fefcf8` (parchment) with a `3px` gold left border
- Text: dark (`var(--text)`), not white
- Feels like a margin annotation rather than a system alert
- Subtle warm box-shadow instead of colored backgrounds

### Progress Bar
- Color: `var(--accent)` (gold) instead of blue
- Track: `rgba(139,105,20,0.1)`

## Scope & Constraints

- **Single file change:** `knowledgeweaver/ui/web/index.html`
- **No backend changes** — all API endpoints, polling logic, and data structures remain identical
- **Google Fonts CDN** — requires internet connection to load fonts; graceful fallback to Georgia/serif
- **No new dependencies** — pure HTML/CSS/JS, no build step
- **Accessibility preserved** — all ARIA labels, roles, and keyboard navigation retained from current implementation
- **Animations preserved** — bubble float, progress bar, pulse dot, toast slide-in/out all kept; colors updated

## What Does NOT Change

- API endpoints (`/api/queries`, `/api/recommendations`, `/outputs/`)
- JavaScript logic (polling, toast system, bubble cloud rendering, query card rendering)
- HTML structure and ARIA attributes
- Responsive behavior
- Feature set
