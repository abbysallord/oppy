# Oppy Web UI Brand Identity & Design System Specification

This document defines the visual parameters, typography, color palettes, and component layout rules required to build a premium, high-fidelity Web UI for Oppy.

---

## 🎨 1. Color Palette System

All interfaces should adhere strictly to this curated color palette. Avoid pure blacks (`#000000`) and pure whites (`#FFFFFF`) to maintain a premium contrast and avoid visual fatigue.

| Token | HEX | Role / Usage |
| :--- | :--- | :--- |
| **Brand Primary (Accent)** | `#D946EF` (Magenta) | Headings, active states, key interactive highlights, brand logo. |
| **Brand Secondary** | `#06B6D4` (Cyan) | Interactive anchors, category badges, focus states, secondary buttons. |
| **Neutral Dark (Background)**| `#0F172A` (Slate 900)| Primary background across all pages. |
| **Neutral Card (Surface)** | `#1E293B` (Slate 800)| Cards, panels, input fields, navigation menus. |
| **Neutral Border** | `#334155` (Slate 700)| Borders, divider lines, structure wrappers. |
| **Success (Green)** | `#10B981` (Emerald 500)| "Paid Only" indicators, successful sync indicators. |
| **Warning (Yellow)** | `#F59E0B` (Amber 500) | Impending deadlines, warning banners. |
| **Text Primary** | `#F8FAFC` (Slate 50) | Main content, readable body text, field labels. |
| **Text Muted** | `#94A3B8` (Slate 400) | Secondary subtitles, metadata, metadata descriptors. |

---

## ✍️ 2. Typography

*   **Primary Font Family (Headers & UI)**: **`PP Neue Montreal`** or **`Outfit`** (Fallback: `system-ui, -apple-system, sans-serif`)
    *   *Weight*: Medium (500) / Semi-Bold (600)
    *   *Letter Spacing*: `-0.02em` (for clean tracking)
*   **Secondary Font Family (Data, Code & TUI elements)**: **`JetBrains Mono`** or **`Fira Code`** (Fallback: `monospace`)
    *   *Weight*: Light (300) / Regular (400)
    *   *Role*: Database tables, URLs, search prompts, ASCII art logos.

---

## 📐 3. Layout Grid & Structure

1.  **Chassis (App Shell)**:
    *   Max-width container: `1280px` (`max-w-7xl`).
    *   Padding: `1.5rem` (`p-6`) on desktop, `1rem` (`p-4`) on mobile.
2.  **Cards & Containers**:
    *   Background: `#1E293B` (Slate 800).
    *   Border: `1px solid #334155` (Slate 700).
    *   Shadow: `shadow-xl shadow-slate-950/20`.
    *   Radius: `8px` (`rounded-lg`) — keep it sharp and clean; avoid round bubbles.
3.  **Contrast Rule**:
    *   All buttons and clickable items must have a smooth hover transition: `transition-all duration-200 ease-in-out`.
    *   Hover state for buttons: Scale slightly up (`hover:scale-[1.02]`) and shift color slightly brighter.

---

## 🖥️ 4. Layout Architecture (Pages & Views)

### Page A: Landing & Live Dashboard
*   **Hero Section**:
    *   A centered vector graphic of **Oppy (The Scouting Satellite)** in Magenta/Cyan.
    *   Title: "Automate your internship and hackathon scout."
    *   Call-to-Action: A dark, sleek command block containing:
        `npx @dshenoyh/oppy-cli` (with a "Copy to Clipboard" button).
*   **Live Ledger Panel**:
    *   A real-time list of cached opportunities fetched from the SQLite store.
    *   Features: Case-insensitive search bar, filter pills (`Paid Only`, `Remote Only`, `Platform Selection`).
    *   Table columns: Platform, Title, Compensation, Deadline, and an "Apply" button.

### Page B: Settings Configuration
*   **Export Settings**:
    *   Visual input fields to define the Markdown export directory.
*   **Platform Selection**:
    *   Vibrant, binary toggles (Magenta/Cyan active states) to enable/disable specific sites (Unstop, Devpost, RemoteOK, WeWorkRemotely).

---

## 🛠️ 5. API Data Structure
The backend provides data in this standard JSON schema for opportunities:

```json
{
  "id": 104,
  "title": "Sales Operation Intern",
  "company": "Flow Operations Ltd",
  "platform": "remoteok",
  "opportunity_type": "internship",
  "opportunity_url": "https://remoteok.com/api/...",
  "stipend_or_prize": "$4,000 - $6,000/Month",
  "deadline": "N/A (Apply ASAP)",
  "is_remote": 1,
  "is_paid": 1,
  "discovered_at": "2026-07-23 20:32:13"
}
```
