"""Shared colours and full-screen chrome for the Oppy TUI.

Every screen is composed the same way: a logo header, an optional stats strip,
a body, and a keybind footer. The result is padded so it fills the terminal
vertically and stays centred (and readable) on very wide terminals.
"""

from rich.align import Align
from rich.console import Console, Group
from rich.control import Control
from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

# Palette
ACCENT = "#00ff85"
INFO = "#1e90ff"
WARN = "#f5a524"
DANGER = "#ef4444"
MUTED = "grey50"

# Content always stretches to fill the full terminal width.
MIN_WIDTH = 60

LOGO = r"""
 ██████╗ ██████╗ ██████╗ ██╗   ██╗
██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
██║   ██║██████╔╝██████╔╝ ╚████╔╝
██║   ██║██╔═══╝ ██╔═══╝   ╚██╔╝
╚██████╔╝██║     ██║        ██║
 ╚═════╝ ╚═╝     ╚═╝        ╚═╝
"""

console = Console()


def clear_screen():
    # Control codes rather than spawning `clear`: works inside the alternate
    # screen buffer and avoids a subprocess on every repaint. Nothing to clear
    # when output is redirected.
    if console.is_terminal:
        console.clear()


def enter_fullscreen():
    """Switch to the alternate screen buffer.

    The dashboard repaints a whole frame per keypress. Without this every frame
    would pile up in scrollback; the alt buffer has none, so the app is always
    exactly one page anchored at the top.

    Rich's set_alt_screen() has no nesting guard — it writes the escape code
    unconditionally — so we check first and report whether *we* took ownership.
    """
    if console.is_alt_screen or not console.is_terminal:
        return False
    entered = console.set_alt_screen(True)
    if entered:
        console.show_cursor(False)
    return entered


def exit_fullscreen(entered):
    if entered:
        console.show_cursor(True)
        console.set_alt_screen(False)


def content_width():
    return max(MIN_WIDTH, console.size.width)


def humanize_since(iso_timestamp):
    """Render an ISO timestamp as a compact age, e.g. '2h ago'."""
    if not iso_timestamp:
        return "never"
    try:
        from datetime import datetime
        elapsed = (datetime.now() - datetime.fromisoformat(iso_timestamp)).total_seconds()
    except Exception:
        return "unknown"

    if elapsed < 0:
        return "just now"
    for seconds, suffix in ((86400, "d"), (3600, "h"), (60, "m")):
        if elapsed >= seconds:
            return f"{int(elapsed // seconds)}{suffix} ago"
    return "just now"


def header_panel():
    lines = [line for line in LOGO.split("\n") if line.strip()]
    pad_to = max(len(line) for line in lines)
    logo = "\n".join(line.ljust(pad_to) for line in lines)

    return Panel(
        Group(
            Align.center(Text(logo, style=f"bold {ACCENT}")),
            Text(""),
            Align.center(Text("Terminal-Native Opportunity Scout & Indexer", style=MUTED)),
        ),
        border_style=ACCENT,
        padding=(0, 1),
    )


def truncate(text, width):
    """Clip to width with a trailing ellipsis so grid rows stay one line tall."""
    text = str(text or "")
    return text if len(text) <= width else text[: width - 1] + "…"


def clip_path(path, width):
    """Clip a path from the left so the filename stays visible."""
    path = str(path or "")
    return path if len(path) <= width else "…" + path[-(width - 1):]


def stats_panel(stats):
    """One-line ledger summary: counts by type plus time since last sync."""
    sep = Text("  ·  ", style=MUTED)
    line = Text()

    def add(value, label, style):
        line.append(f"{value}", style=f"bold {style}")
        line.append(f" {label}", style=MUTED)

    add(stats["total"], "indexed", ACCENT)
    line.append_text(sep)
    add(stats["internship"], "internships", INFO)
    line.append_text(sep)
    add(stats["hackathon"], "hackathons", INFO)
    line.append_text(sep)
    add(stats["job"], "jobs", INFO)
    line.append_text(sep)
    line.append("synced ", style=MUTED)
    line.append(stats["last_sync"], style=f"bold {WARN}")

    return Panel(Align.center(line), border_style=MUTED, padding=(0, 1))


def footer_panel(hints):
    """hints: list of (key, description) rendered as a keybind bar."""
    line = Text()
    for index, (key, description) in enumerate(hints):
        if index:
            line.append("   ", style=MUTED)
        line.append(f" {key} ", style=f"bold black on {ACCENT}")
        line.append(f" {description}", style=MUTED)

    return Panel(Align.center(line), border_style=MUTED, padding=(0, 1))


def build_screen(body, hints, stats=None):
    """Compose a full-height Layout: header / stats / body / footer."""
    layout = Layout()
    sections = [Layout(header_panel(), name="header", size=10)]
    if stats is not None:
        sections.append(Layout(stats_panel(stats), name="stats", size=3))
    sections.append(Layout(body, name="body", ratio=1))
    sections.append(Layout(footer_panel(hints), name="footer", size=3))

    layout.split_column(*sections)
    return layout


def body_height(has_stats=False, reserve=0):
    """Rows available to the body once header, stats and footer are subtracted."""
    chrome = 10 + 3 + 1 + reserve  # header + footer + trailing line
    if has_stats:
        chrome += 3
    return max(6, console.size.height - chrome)


def padded(renderable):
    """Pass through — content fills the full terminal width."""
    return renderable


def render(renderable, reserve=0):
    """Paint a renderable so it fills the terminal without scrolling it.

    ``reserve`` keeps rows free at the bottom for a prompt.
    """
    console.print(
        padded(renderable),
        height=max(1, console.size.height - 1 - reserve),
    )


def render_screen(body, hints, stats=None, reserve=0):
    # Inside the alt buffer a full-height frame repaints over itself: homing the
    # cursor instead of clearing avoids the flash that a clear-then-draw causes
    # at animation rates. Short frames still need a real clear so no stale rows
    # survive underneath.
    if console.is_alt_screen and not reserve:
        console.control(Control.home())
    else:
        clear_screen()
    render(build_screen(body, hints, stats), reserve=reserve)
