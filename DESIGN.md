# Oppy — Design System

Source of truth for every Oppy web surface. Derived from `Oppy_Web_UI_Brand_Identity.md`. Keep all pages consistent with this.

## Concept
Mission-control telemetry meets neon signal. Oppy = scouting satellite. Motifs: radar sweep, orbital rings, signal pings, HUD/telemetry readouts, scan lines. NOT editorial-magazine, NOT generic dark SaaS.

## Color (OKLCH-authored, shipped as hex to match brand doc)
| Token | Hex | Use |
|---|---|---|
| `--bg` | `#0F172A` | page background |
| `--bg-deep` | `#0B1120` | back layer / insets |
| `--surface` | `#1E293B` | cards, panels, inputs, nav |
| `--border` | `#334155` | borders, dividers |
| `--primary` (magenta) | `#D946EF` | brand, headings accents, active, logo, primary signal |
| `--secondary` (cyan) | `#06B6D4` | links, badges, focus, secondary signal |
| `--success` | `#10B981` | "Paid" / synced |
| `--warning` | `#F59E0B` | deadlines / warnings |
| `--ink` | `#F8FAFC` | body text |
| `--muted` | `#94A3B8` | metadata, subtitles |

Body text is `--ink` (contrast ≥ 12:1 on `--bg`). `--muted` only for large/secondary text (≥4.5:1 on bg — OK). Magenta/cyan are for accents & large text, never small body.

## Type
- **Outfit** (500/600, tracking `-0.02em`) — headings & UI. Committed brand identity.
- **JetBrains Mono** (300/400/600) — data, commands, URLs, telemetry, section tags, ASCII.
- Heading scale: fluid `clamp()`, ratio ≥1.25, display max ~5rem. `text-wrap: balance` on h1–h3.

## Layout
- Container `max-w-7xl` (1280px). Desktop pad `p-6`, mobile `p-4`.
- Radius **8px** everywhere — sharp & clean, no bubbles.
- Cards: `--surface` bg, `1px --border`, `shadow-xl shadow-slate-950/20`. No nested cards. No side-stripe borders.

## Motion
- Buttons: `transition-all 200ms ease-out`, hover `scale-[1.02]` + brighten + magenta/cyan glow.
- Signature motion: radar sweep (rotating conic), orbiting pings, typed command, count-up telemetry, per-section scroll reveals (varied, not uniform), signal-line draw on the how-it-works timeline.
- Every animation has a `prefers-reduced-motion: reduce` fallback (static/crossfade).

## Components (shared)
Command block (copy button), filter pills (magenta/cyan active glow), live ledger table (Platform · Title · Compensation · Deadline · Apply), toggles, badges (Paid=emerald, Remote=cyan, deadline-soon=amber).
