# UI_PORTAL.md — SnapStudy Portal visual design (feature P3b)

> Addendum to `AGENT.md` and `AGENT_PORTAL.md`. It changes **how the portal looks**, nothing else.
> No backend, API, database or auth changes. If this file and `AGENT*.md` disagree on anything
> that is not purely visual, `AGENT*.md` wins.

Style name: **Red Noir**. A dark, calm, data-first interface with one red accent, inspired by the
reference at `docs/ui-reference-red-noir.html` (style inspiration only).

---

## 0. How to work

Same loop as `AGENT.md` Section 0: announce, short plan, implement, self-check, report (✅ built,
🧪 how I test it, 🧠 how it works in 3 lines, ⚠️ limits, ➡️ next, and the **Bot regression check**
line), then **STOP**. One feature: **P3b**. Do not build ahead. Do not add pages, routes or API calls.

---

## 1. Principles

1. **A data app, not a landing page.** Every number, label and date comes from the real API. No
   invented stats, people, testimonials, pricing or logos.
2. **Phone first.** Students arrive from Telegram on a phone. Design for 360 px, then scale up.
3. **Calm.** One accent colour (red). Static backgrounds. Motion only where it helps.
4. **Honest states.** Loading, empty, error and logged out are designed, not afterthoughts.
5. **Bangla must render.** Fonts and line-heights are chosen so Bangla never shows empty boxes or clips.
6. **Plain and small.** Plain CSS and React. No Tailwind, no UI kit, no chart library.

### What to take from the reference, and what to leave

| Take | Leave out |
|---|---|
| Near-black base with a warm red tint at the top | Animated star field, parallax |
| Red accent `#ef233c` with a soft glow | Pricing, testimonials, logo strip, waitlist |
| Glass pill navbar (blur plus 1px border) | Giant outlined footer text |
| Bento-style cards with subtle borders | Tailwind, CDN scripts, iconify |
| Gradient page titles | Fake product copy and fake metrics |
| One shiny-border primary button | More than one animated element at a time |

---

## 2. Stack rules (unchanged from AGENT_PORTAL.md section 9)

- React + Vite, plain JavaScript (JSX), `react-router-dom`, `fetch`, **plain CSS** in `styles.css`.
- Icons: small inline SVG components in `components/Icon.jsx`. No icon library.
- **Only new dependencies allowed:** self-hosted fonts through `@fontsource`:
  - `@fontsource-variable/manrope` (headings)
  - `@fontsource-variable/inter` (body)
  - `@fontsource/noto-sans-bengali` (Bangla fallback)
  Reason: no CDN requests, works offline in the browser cache, and Manrope/Inter have no Bengali glyphs.
  State this in the report.
- Never `dangerouslySetInnerHTML`. Show model text with `white-space: pre-wrap`.
- No auth in JavaScript storage. The session stays in the HttpOnly cookie.

---

## 3. Design tokens

Put these in `:root` in `styles.css`. Components use variables only, never raw colours.

```css
:root {
  /* surfaces */
  --bg: #050506;
  --bg-tint: #1a0505;
  --card-from: rgba(24, 24, 27, 0.60);
  --card-to: #000000;
  --card-border: rgba(255, 255, 255, 0.10);
  --card-border-hover: rgba(255, 255, 255, 0.20);
  --glass: rgba(0, 0, 0, 0.60);

  /* text */
  --text: #ffffff;
  --text-2: #a1a1aa;
  --text-3: #71717a;

  /* accent */
  --accent: #ef233c;
  --accent-light: #ff4d62;        /* small red text on dark */
  --accent-glow: rgba(239, 35, 60, 0.35);
  --accent-soft: rgba(239, 35, 60, 0.12);

  /* semantic (used sparingly) */
  --ok: #34d399;
  --warn: #fbbf24;

  /* shape and spacing */
  --radius-card: 16px;
  --radius-pill: 9999px;
  --gap: 16px;
  --content-max: 960px;

  /* type */
  --font-head: "Manrope Variable", "Noto Sans Bengali", "Nirmala UI", system-ui, sans-serif;
  --font-body: "Inter Variable", "Noto Sans Bengali", "Nirmala UI", system-ui, sans-serif;
}
```

### Type scale

| Use | Size / weight | Notes |
|---|---|---|
| Page title | 28px (mobile) to 36px, 700, Manrope | Gradient text (white to 60%), tracking -0.02em |
| Section title | 18px to 20px, 600, Manrope | Plain white |
| KPI number | 32px, 700, Manrope | Tabular numerals |
| Body | 15px, 400, Inter | Line-height 1.6 |
| Small / label | 13px, 500, Inter, `--text-2` | |
| Bangla text | Body size +1px, line-height 1.75 | Apply with `:lang(bn)` |

### Background

On `body`:
1. Solid `--bg`.
2. A top gradient from `--bg-tint` to transparent, about 480px tall.
3. A faint 40px grid (`rgba(255,255,255,0.03)` lines) masked to fade out at the edges.

All static. No animated background.

### Motion

- **Page mount:** fade-up, 8px, 350ms, once.
- **Primary CTA:** slow rotating border highlight (conic gradient), only on the Practice button.
- Hover: border brightens, 150ms.
- `@media (prefers-reduced-motion: reduce)`: turn off every animation and transition.

---

## 4. Components (`web/src/components/`)

Keep the existing `Layout`, `Card`, `EmptyState`, `ErrorState`, `Bars`. Restyle them, and add:

| Component | Purpose |
|---|---|
| `Icon.jsx` | Inline SVG icons: bolt (logo), home, notes, target, chart, settings, arrow-right, calendar, check, alert, logout |
| `Badge.jsx` | Small pill. Variants: `neutral` (language), `ok` (quiz ready, score), `warn` (quiz preparing), `accent` |
| `KpiCard.jsx` | Label, big value, optional footer (progress bar). Value can be `—` |
| `ProgressBar.jsx` | 6px bar for accuracy, with `role="progressbar"` and `aria-valuenow` |
| `PracticeCard.jsx` | The state-driven practice block (section 5.1) |
| `NoteCard.jsx` | Title, language badge, quiz status badge, last score, relative date |
| `Skeleton.jsx` | Shimmer-free grey blocks in the same shape as the real card |
| `ShinyButton.jsx` | The one animated primary CTA. Renders an `<a>` (deep link) or `<button>` |

### Layout

**Phone (under 768px):**
- Top bar: logo mark, "SnapStudy AI" and a small PORTAL badge, with the user's name on the right (truncated).
- **Bottom tab bar** (fixed, glass, `padding-bottom: env(safe-area-inset-bottom)`): Dashboard, Notes, Settings. Leave room for Weak, Mistakes and History tabs (P4) without redesign.
- Page content has `padding-bottom` equal to the tab bar height.

**Tablet and desktop (768px and up):**
- Floating **glass pill navbar** at the top, centred, max width 960px: logo on the left, links in the middle, user name on the right. Active link has `--accent-soft` background and `--text` colour.
- No bottom tab bar.

Declare `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`.

---

## 5. Pages

Routes, data and API stay exactly as they are.

### 5.1 Dashboard

```
┌───────────────────────────────────────┐
│ Study Dashboard                        │   gradient title
│ Hi, <first name>. Here is your progress│
│                                        │
│ ┌────────┐ ┌────────┐                  │   2 columns on phone,
│ │ Notes  │ │Quizzes │                  │   4 columns on desktop
│ │   1    │ │   0    │                  │
│ └────────┘ └────────┘                  │
│ ┌────────┐ ┌────────┐                  │
│ │Accuracy│ │ Weak   │                  │
│ │ ▬▬▬ 72%│ │topics 2│                  │
│ └────────┘ └────────┘                  │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │ 🎯 Practice (state-driven card)    │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Recent notes                View all → │
│ ┌────────────────────────────────────┐ │
│ │ <title>              [EN] [Quiz ✓] │ │
│ │ 📅 2 hours ago        Last: 4/5    │ │
│ └────────────────────────────────────┘ │
└───────────────────────────────────────┘
```

**KPI rules**
- Notes: the count.
- Quizzes taken: the count.
- Accuracy: `—` when there is no quiz yet, otherwise `NN%` with a `ProgressBar`.
- Weak topics: `—` until at least one quiz exists. A real `0` is shown in `--ok` only after quizzes exist.

**Practice card states** (real data only):

| Data | What the card shows |
|---|---|
| Mistakes > 0 | "You have N questions to fix." plus the **ShinyButton** "Practice in Telegram" (deep link `https://t.me/<bot>?start=practice`) |
| Quizzes = 0 | "Take your first quiz in Telegram." plus a plain secondary link "Open the bot" |
| Quizzes > 0 and no mistakes | "No mistakes to practice 🎉" with **no button** |

If the dashboard API does not return a mistakes count, use the weak-topics count as the condition and
say so in the report. Do not add or change an endpoint.

**Empty dashboard (no notes):** `EmptyState` with the text "Send a photo of your notes to the bot to get
started" and a link to `https://t.me/<bot_username>`.

### 5.2 Notes list

- Page title "Notes". A vertical list of `NoteCard`.
- Each card is one tappable link to the note detail. Sorted as the API returns it.
- Empty state as above. Loading shows 3 skeleton cards.

### 5.3 Note detail

- Back link, title, meta row (language badge, relative date, last score).
- **Summary** card: `white-space: pre-wrap`, body font, Bangla styles applied when the note language is `bn`.
- **Quiz** card: status (ready / preparing), past scores as small badges. Quizzes are taken in Telegram,
  so the button deep-links to the bot.
- Unknown or foreign note id: the API returns 404, so show the "Note not found" error state.

### 5.4 Settings

- Cards for name, language (read only), and a **Log out** button (secondary style, not red).
- A short privacy line: "Photos are not stored. The AI-generated summary and quiz are saved, and only you can see them."

### 5.5 Login and state screens

- Login: centred card on the same background, a short message while exchanging the token.
- Expired or used link: "This link expired. Send /portal to the bot to get a new one."
- 401 anywhere: "Your session ended. Send /portal to the bot to get a new link." No redirect loops.
- Error: icon, one sentence, a Retry button.

### 5.6 Future pages (P4), so the style is ready

Weak topics: rows with topic, `ProgressBar`, accuracy and attempts, worst first, weak ones tagged `accent`.
Mistake notebook: collapsible question cards with the correct option highlighted in `--ok`.
History: the `Bars` chart drawn in CSS or SVG, bars in `--accent`, axis text in `--text-3`.

---

## 6. Bugs to fix in this feature (seen in the live portal)

### 6.1 "Invalid Date"
SQLite `CURRENT_TIMESTAMP` returns `YYYY-MM-DD HH:MM:SS` in UTC with no timezone, which browsers parse
unreliably. Add **one** helper in `web/src/format.js` and use it everywhere:

```js
export function parseDbDate(value) {
  if (!value) return null;
  const iso = String(value).includes("T") ? String(value) : String(value).replace(" ", "T");
  const d = new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(iso) ? iso : iso + "Z");
  return Number.isNaN(d.getTime()) ? null : d;
}

export function timeAgo(value, locale = navigator.language) {
  const d = parseDbDate(value);
  if (!d) return "—";
  const diff = (d.getTime() - Date.now()) / 1000;
  const units = [["day", 86400], ["hour", 3600], ["minute", 60]];
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });
  for (const [unit, secs] of units) {
    if (Math.abs(diff) >= secs) return rtf.format(Math.round(diff / secs), unit);
  }
  return rtf.format(0, "minute");
}

export function fullDate(value, locale = navigator.language) {
  const d = parseDbDate(value);
  return d ? d.toLocaleString(locale, { dateStyle: "medium", timeStyle: "short" }) : "—";
}
```

Show `timeAgo(...)` as the text and `fullDate(...)` in the `title` attribute. Never print "Invalid Date".

### 6.2 "Study Note #1"
Title helper (`web/src/format.js`):
1. `note.title` if it is non-empty.
2. Otherwise the first non-empty line of the summary after removing a leading emoji heading such as "📝 Summary", trimmed to about 60 characters.
3. Otherwise "Untitled note".

### 6.3 Weak topics "0" in green with no quizzes
See the KPI rules in 5.1.

### 6.4 Practice button with nothing to practice
See the Practice card states in 5.1.

---

## 7. Accessibility and quality bar

- Touch targets at least **44 × 44px**.
- Text contrast at least **WCAG AA**. Use `--accent-light` (not `--accent`) for small red text.
- Visible **focus ring** (2px `--accent`, 2px offset) on every interactive element.
- Real `<a>`, `<button>`, `<nav>`, `<main>`. Icon-only buttons have `aria-label`. Progress bars have ARIA values.
- Set `<html lang>` from the user's language (`en` or `bn`).
- Skeletons for loading (same shape as real content), not spinners.
- No layout shift: reserve space for cards and the tab bar.
- Respect `prefers-reduced-motion`.
- Keep the CSS under about 600 lines. No unused styles.
- The label **"(sample data)"** stays visible for the seeded demo user.

---

## 8. Files to touch

```
web/
├── package.json                 add the 3 @fontsource packages
└── src/
    ├── main.jsx                 import the font CSS files
    ├── styles.css               tokens, background, layout, components
    ├── format.js                NEW: parseDbDate, timeAgo, fullDate, noteTitle
    ├── App.jsx                  only if the layout wrapper needs a change
    ├── pages/                   restyle Login, Dashboard, Notes, NoteDetail, Settings
    └── components/              Layout, Card, EmptyState, ErrorState, Bars (restyle)
                                 + Icon, Badge, KpiCard, ProgressBar, PracticeCard,
                                   NoteCard, Skeleton, ShinyButton (new)
```

Do not touch `app/`, `portal/`, the database, or the tests (other than running them).

---

## 9. Acceptance criteria and human test

**Done when:**
- [ ] `cd web && npm ci && npm run build` succeeds with no new warnings
- [ ] No "Invalid Date" anywhere, and relative dates show with a full-date tooltip
- [ ] No "Study Note #N" fallback titles
- [ ] KPI cards and the Practice card follow the state tables in 5.1
- [ ] Bottom tab bar on phone, glass pill navbar on desktop
- [ ] Only one animated element (the Practice CTA), and none with reduced motion on
- [ ] No Tailwind, CDN script or icon library added. Only the 3 font packages
- [ ] Isolation tests from `AGENT_PORTAL.md` section 13 still pass
- [ ] Bot regression check: photo → summary → quiz still works

**Human test (phone, 360px wide, plus desktop):**
1. Send `/portal`, open the link, and check the dashboard with real data.
2. With a fresh account, check the empty dashboard and the "first quiz" Practice card state.
3. Take a quiz with some wrong answers, reload, and check the mistakes count, the Practice CTA and accuracy.
4. Open a **Bangla** note: no empty boxes, no clipped lines.
5. Open the same link twice: friendly expired message.
6. Turn on "reduce motion" in the OS and check that nothing animates.
7. Log out, press back: "Your session ended…", not a blank screen.

---

## 10. Prompt to give the coding agent

```
Read AGENT.md Section 0, AGENT_PORTAL.md (especially section 9) and UI_PORTAL.md completely.
Do ONLY feature P3b (visual redesign of the portal) exactly as UI_PORTAL.md describes. Open
docs/ui-reference-red-noir.html for style inspiration only; do not copy its content or branding.
No backend, API, database or auth changes. Plain CSS, no new dependencies except the three
@fontsource packages (say why). Fix the four bugs in section 6. When done, report in the usual format
with exact phone and desktop test steps, the 3-line "how it works", the dependency list, and the
"Bot regression check" line. Then stop.
```
