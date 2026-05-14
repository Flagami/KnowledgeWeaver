# KnowledgeWeaver Frontend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign `knowledgeweaver/ui/web/index.html` from Apple-style to an academic/scholarly editorial aesthetic — warm ivory palette, Cormorant Garamond + EB Garamond typography, gold accents.

**Architecture:** Single-file change. All CSS, HTML, and JS live inline in `index.html`. No backend changes, no new dependencies. Google Fonts loaded via CDN `<link>` tag. All API endpoints, polling logic, and data structures remain identical.

**Tech Stack:** HTML5, CSS3 (custom properties, backdrop-filter, keyframe animations), vanilla JS ES6+, Google Fonts CDN (Cormorant Garamond, EB Garamond, Courier Prime).

---

### Task 1: Add Google Fonts and replace CSS custom properties

**Files:**
- Modify: `knowledgeweaver/ui/web/index.html:3-27` (head + :root block)

- [ ] **Step 1: Add Google Fonts link after the `<meta viewport>` tag**

Replace this line in `<head>`:
```html
  <title>KnowledgeWeaver — AI Research Synthesis</title>
```
With:
```html
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Courier+Prime:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
  <title>KnowledgeWeaver — AI Research Synthesis</title>
```

- [ ] **Step 2: Replace the entire `:root` block**

Replace the existing `:root { ... }` block (lines 10–27) with:
```css
    :root {
      --bg: #faf8f4;
      --card: #fefcf8;
      --primary: #8b6914;
      --primary-hover: #7a5c10;
      --success: #2d6a2d;
      --success-text: #2d6a2d;
      --error: #8b2020;
      --warning: #8b5e14;
      --text: #1a1209;
      --muted: #6b5c3e;
      --border: rgba(139,105,20,0.12);
      --rule: #c9a84c;
      --radius-card: 6px;
      --radius-input: 4px;
      --radius-badge: 4px;
      --shadow-card: 0 1px 4px rgba(139,105,20,0.08), 0 0 0 1px rgba(139,105,20,0.06);
      --mono: 'Courier Prime', 'Courier New', monospace;
      --serif: 'EB Garamond', Georgia, serif;
      --display: 'Cormorant Garamond', Georgia, serif;
    }
```

- [ ] **Step 3: Verify fonts load**

Start the server: `cd /Users/zmore/ClaudeProject/KnowledgeWeaver && python run_web_ui.py`
Open `http://localhost:8000` in a browser. Open DevTools → Network tab → filter by "fonts.googleapis". Confirm 3 font requests appear (Cormorant Garamond, EB Garamond, Courier Prime).

- [ ] **Step 4: Commit**
```bash
git add knowledgeweaver/ui/web/index.html
git commit -m "feat: add Google Fonts and update CSS color/font variables for editorial redesign"
```

---

### Task 2: Update body, typography base, and card styles

**Files:**
- Modify: `knowledgeweaver/ui/web/index.html` (body, .card, .section-label, .explore-prompt, .library-heading)

- [ ] **Step 1: Replace the `body` rule**

```css
    body {
      font-family: var(--serif);
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.6;
    }
```

- [ ] **Step 2: Replace the `.card` rule**

```css
    .card {
      background: var(--card);
      border-radius: var(--radius-card);
      box-shadow: var(--shadow-card);
      padding: 32px;
      margin-bottom: 24px;
    }
```

- [ ] **Step 3: Replace the `.section-label` rule**

```css
    .section-label {
      font-family: var(--serif);
      font-size: 0.8rem;
      font-weight: 500;
      font-variant: small-caps;
      letter-spacing: 0.04em;
      text-transform: none;
      color: var(--muted);
      margin-bottom: 14px;
    }
```

- [ ] **Step 4: Replace the `.explore-prompt` rule**

```css
    .explore-prompt {
      font-family: var(--display);
      font-size: 1.8rem;
      font-weight: 400;
      font-style: italic;
      color: var(--text);
      margin-bottom: 20px;
      letter-spacing: -0.01em;
      line-height: 1.2;
    }
```

- [ ] **Step 5: Replace the `.library-heading` rule**

```css
    .library-heading {
      font-family: var(--display);
      font-size: 1.4rem;
      font-weight: 400;
      font-style: italic;
      color: var(--text);
      margin-bottom: 16px;
      letter-spacing: -0.01em;
    }
```

- [ ] **Step 6: Verify in browser**

Reload `http://localhost:8000`. The page heading should now render in Cormorant Garamond italic. Section labels ("Explore", "Research Library") should appear in small-caps EB Garamond.

- [ ] **Step 7: Commit**
```bash
git add knowledgeweaver/ui/web/index.html
git commit -m "feat: apply editorial serif typography to body, headings, and section labels"
```

---

### Task 3: Redesign the header

**Files:**
- Modify: `knowledgeweaver/ui/web/index.html` (header CSS + header HTML)

- [ ] **Step 1: Replace the `header` CSS rule**

```css
    header {
      background: rgba(250,248,244,0.92);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-bottom: none;
      padding: 0 32px;
      height: 52px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    header::after {
      content: '';
      position: absolute;
      bottom: 0; left: 0; right: 0;
      height: 1px;
      background: var(--rule);
      opacity: 0.35;
    }
```

- [ ] **Step 2: Replace the `.logo` and `.logo-icon` CSS rules**

Remove the entire `.logo-icon { ... }` rule. Replace `.logo { ... }` with:
```css
    .logo {
      font-family: var(--display);
      font-style: italic;
      font-size: 1.15rem;
      font-weight: 400;
      color: var(--text);
      letter-spacing: 0.01em;
    }
```

- [ ] **Step 3: Replace the `.active-indicator` CSS rule**

```css
    .active-indicator {
      display: none;
      align-items: center;
      gap: 6px;
      font-family: var(--serif);
      font-style: italic;
      font-size: 0.82rem;
      color: var(--muted);
    }
```

- [ ] **Step 4: Replace the header HTML**

Replace the entire `<header>` block in the HTML body:
```html
<header>
  <div class="logo">KnowledgeWeaver</div>
  <span class="active-indicator" id="activeIndicator">
    <span class="pulse-dot" aria-hidden="true"></span>
    <span id="activeCount">0</span> researching…
  </span>
</header>
```

- [ ] **Step 5: Verify in browser**

Reload `http://localhost:8000`. The header should show "KnowledgeWeaver" in italic Cormorant Garamond with a faint gold hairline rule underneath. No icon.

- [ ] **Step 6: Commit**
```bash
git add knowledgeweaver/ui/web/index.html
git commit -m "feat: redesign header with italic serif logo and gold hairline rule"
```

---

### Task 4: Redesign input field and Explore button

**Files:**
- Modify: `knowledgeweaver/ui/web/index.html` (`.query-input`, `.btn-explore` CSS)

- [ ] **Step 1: Replace the `.query-input` CSS rule**

```css
    .query-input {
      flex: 1;
      padding: 11px 14px;
      border: 1px solid var(--border);
      border-radius: var(--radius-input);
      font-size: 1rem;
      font-family: var(--serif);
      color: var(--text);
      background: var(--card);
      outline: none;
      transition: border-color .15s;
    }
    .query-input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: none;
      background: #fff;
    }
    .query-input::placeholder { color: var(--muted); font-style: italic; }
```

- [ ] **Step 2: Replace the `.btn-explore` CSS rules**

```css
    .btn-explore {
      padding: 11px 22px;
      background: transparent;
      color: var(--primary);
      border: 1.5px solid var(--primary);
      border-radius: var(--radius-input);
      font-size: 0.95rem;
      font-family: var(--serif);
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: background .15s, color .15s, opacity .15s;
      display: flex; align-items: center; gap: 6px;
    }
    .btn-explore:hover:not(:disabled) { background: var(--primary); color: #fefcf8; }
    .btn-explore:active:not(:disabled) { opacity: .85; }
    .btn-explore:disabled { opacity: .35; cursor: not-allowed; }
```

- [ ] **Step 3: Verify in browser**

Reload `http://localhost:8000`. The input placeholder should be italic. The Explore button should be outlined gold, filling gold on hover.

- [ ] **Step 4: Commit**
```bash
git add knowledgeweaver/ui/web/index.html
git commit -m "feat: redesign input and explore button with editorial outlined style"
```

---

### Task 5: Redesign bubble cloud

**Files:**
- Modify: `knowledgeweaver/ui/web/index.html` (`.bubble` CSS + `BUBBLE_SCHEMES` + `bubbleSizeForWeight` + `renderWordCloud` in JS)

- [ ] **Step 1: Replace the `.bubble` CSS rule**

```css
    .bubble {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 50px;
      cursor: pointer;
      font-family: var(--display);
      font-weight: 400;
      text-align: center;
      line-height: 1.3;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      animation: bubbleFloat var(--dur) ease-in-out infinite;
      animation-delay: var(--delay);
      word-break: break-word;
      hyphens: auto;
      background: #fefcf8;
      border: 1px solid rgba(139,105,20,0.25);
      color: var(--text);
      box-shadow: 0 1px 4px rgba(139,105,20,0.06);
    }
    .bubble:hover {
      transform: scale(1.06) !important;
      box-shadow: 0 4px 16px rgba(139,105,20,0.15) !important;
    }
    .bubble:focus-visible {
      outline: 2px solid var(--primary);
      outline-offset: 3px;
    }
```

- [ ] **Step 2: Replace `BUBBLE_SCHEMES` in the JS section**

```js
const BUBBLE_SCHEMES = [
  { bg: '#fefcf8', text: '#1a1209' },
  { bg: '#fdf8ee', text: '#5c3d0a' },
  { bg: '#f8f4ec', text: '#3d2c0a' },
  { bg: '#fefaf2', text: '#6b4c14' },
  { bg: '#f5f0e8', text: '#2d1f08' },
  { bg: '#faf6ed', text: '#4a3510' },
];
```

- [ ] **Step 3: Replace `bubbleSizeForWeight` to use padding-based sizing for pill shapes**

```js
function bubbleSizeForWeight(w) {
  if (w <= 2) return { font: '0.85rem', padding: '9px 18px' };
  if (w <= 4) return { font: '0.95rem', padding: '10px 22px' };
  if (w <= 6) return { font: '1.05rem', padding: '11px 26px' };
  if (w <= 8) return { font: '1.15rem', padding: '12px 30px' };
  return { font: '1.25rem', padding: '13px 34px' };
}
```

- [ ] **Step 4: Update `renderWordCloud` to use padding instead of width/height**

In the `renderWordCloud` function, replace the `bubble.style.cssText` assignment:
```js
    const { font, padding } = bubbleSizeForWeight(kw.weight || 5);
    // ...
    bubble.style.cssText = [
      `background:${scheme.bg}`,
      `color:${scheme.text}`,
      `font-size:${font}`,
      `padding:${padding}`,
      `--dur:${dur}`,
      `--delay:${delay}`,
    ].join(';');
```

- [ ] **Step 5: Verify in browser**

Reload `http://localhost:8000`. Bubbles should now be pill/oval shaped with warm cream fills and subtle gold borders. Text should render in Cormorant Garamond.

- [ ] **Step 6: Commit**
```bash
git add knowledgeweaver/ui/web/index.html
git commit -m "feat: redesign bubble cloud as editorial pill shapes with warm serif typography"
```

---

### Task 6: Redesign research library cards and badges

**Files:**
- Modify: `knowledgeweaver/ui/web/index.html` (`.query-card`, `.badge-*`, `.query-*`, `.empty-state` CSS + `renderQueryCard` JS)

- [ ] **Step 1: Replace the `.query-card` CSS rule**

```css
    .query-card {
      padding: 14px 16px;
      background: transparent;
      transition: background .12s;
      position: relative;
      overflow: hidden;
      border-left: 3px solid transparent;
    }
    .query-card + .query-card {
      border-top: 1px solid rgba(139,105,20,0.08);
    }
    .query-card:hover { background: rgba(139,105,20,0.02); }
    .query-card.is-processing { border-left-color: var(--rule); }
```

- [ ] **Step 2: Replace all `.badge-*` CSS rules**

```css
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-family: var(--serif);
      font-variant: small-caps;
      font-size: 0.82rem;
      font-weight: 500;
      white-space: nowrap;
      flex-shrink: 0;
      background: none;
      padding: 0;
    }
    .badge-pending    { color: var(--muted); }
    .badge-processing { color: var(--primary); font-style: italic; }
    .badge-completed  { color: #2d6a2d; }
    .badge-failed     { color: #8b2020; }
```

- [ ] **Step 3: Replace `.query-text`, `.query-timestamp`, `.query-report`, `.query-error`, `.empty-state` CSS**

```css
    .query-text {
      font-family: var(--serif);
      font-weight: 500;
      font-size: 0.95rem;
      color: var(--text);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
      min-width: 0;
    }
    .query-timestamp {
      font-family: var(--mono);
      font-size: 0.72rem;
      color: var(--muted);
    }
    .query-report {
      font-family: var(--serif);
      font-size: 0.88rem;
      color: var(--primary);
      text-decoration: none;
      font-weight: 400;
      background: none;
      border: none;
      cursor: pointer;
      padding: 0;
    }
    .query-report:hover { text-decoration: underline; }
    .query-error {
      font-family: var(--mono);
      font-size: 0.72rem;
      color: #8b2020;
    }
    .empty-state {
      text-align: center;
      color: var(--muted);
      font-family: var(--display);
      font-style: italic;
      font-size: 1rem;
      padding: 32px 0;
    }
```

- [ ] **Step 4: Update `renderQueryCard` in JS to add `is-processing` class**

In the `renderQueryCard` function, after `card.dataset.queryId = query.query_id;`, add:
```js
  if (query.status === 'processing') card.classList.add('is-processing');
```

- [ ] **Step 5: Update empty state text in `renderQueryList`**

```js
list.innerHTML = '<p class="empty-state">No research yet. Enter a topic above to begin.</p>';
```

- [ ] **Step 6: Verify in browser**

Reload `http://localhost:8000`. Processing items should show a gold left border. Badges should be small-caps serif with no background. Empty state should be italic Cormorant Garamond.

- [ ] **Step 7: Commit**
```bash
git add knowledgeweaver/ui/web/index.html
git commit -m "feat: redesign research library with editorial badges and gold processing indicator"
```

---

### Task 7: Redesign toast notifications and progress bar

**Files:**
- Modify: `knowledgeweaver/ui/web/index.html` (`.toast`, `.progress-bar-*` CSS)

- [ ] **Step 1: Replace all `.toast` CSS rules**

```css
    .toast {
      pointer-events: auto;
      padding: 12px 16px;
      border-radius: var(--radius-input);
      font-family: var(--serif);
      font-size: 0.9rem;
      font-weight: 400;
      color: var(--text);
      background: #fefcf8;
      max-width: 320px;
      box-shadow: 0 2px 12px rgba(139,105,20,0.12);
      animation: slideIn .25s ease-out forwards;
      display: flex;
      align-items: center;
      gap: 10px;
      border-left: 3px solid var(--rule);
    }
    .toast.toast-success { border-left-color: #2d6a2d; }
    .toast.toast-error   { border-left-color: #8b2020; }
    .toast.toast-info    { border-left-color: var(--primary); }
    .toast.toast-hide    { animation: slideOut .25s ease-in forwards; }
```

- [ ] **Step 2: Replace `.progress-bar-track` and `.progress-bar-fill` CSS**

```css
    .progress-bar-track {
      position: absolute;
      bottom: 0; left: 0; right: 0;
      height: 2px;
      background: rgba(139,105,20,0.1);
    }
    .progress-bar-fill {
      height: 100%;
      background: var(--primary);
      animation: progressIndeterminate 1.8s ease-in-out infinite;
      transform-origin: left;
    }
```

- [ ] **Step 3: Verify in browser**

Submit a test query (or wait for a processing one). Toast notifications should appear as parchment cards with a colored left border and dark text. The progress bar at the bottom of processing cards should be gold.

- [ ] **Step 4: Final visual pass**

Check all states in the browser:
- Empty state (no queries)
- Processing query (gold left border, gold progress bar, italic badge)
- Completed query (green badge, "Open Report ↗" link)
- Failed query (red badge, error text)
- Bubble cloud (pill shapes, warm cream, serif text)
- Toast notifications (parchment, left border)
- Header (italic serif logo, hairline gold rule)

- [ ] **Step 5: Commit**
```bash
git add knowledgeweaver/ui/web/index.html
git commit -m "feat: redesign toast notifications and progress bar with editorial warm palette"
```
