"""Shared colours, spacing and formatting for every screen.

Mirrors the Figma wireframes: warm off-white canvas, near-black ink for
primary actions, muted grey-green for secondary text, and thin grey borders.
"""

import flet as ft

# ---- colour ---------------------------------------------------------------
# MUTED is one step darker than the wireframe grey so secondary text clears
# WCAG AA (4.5:1) on both BG and SURFACE.
BG = "#F5F7F2"
SURFACE = "#FFFFFF"
INK = "#1B2A23"
MUTED = "#57655D"
BORDER = "#D5DCD5"
NOTE_BG = "#ECEFEA"
WARN_BG = "#F3EFE2"
ERROR = "#B3261E"
SUCCESS = "#2E6B4F"
ACCENT_MOOD = "#C9A227"

# Text placed on top of INK (dark cards) — BORDER is too dim for body copy.
ON_INK = "#D5DCD5"
ON_INK_MUTED = "#A9B5AD"

# ---- shape ----------------------------------------------------------------
RADIUS = 8
RADIUS_SM = 6
RADIUS_PILL = 999
PAD = 20

# ---- spacing --------------------------------------------------------------
SPACE_XS = 4
SPACE_S = 8
SPACE_M = 12
SPACE_L = 16
SPACE_XL = 24
PAGE_PAD = 16

# ---- type scale -----------------------------------------------------------
TITLE_LG = 34
TITLE = 28
TITLE_SM = 26
HEADING = 20
SUBHEAD = 18
BODY = 14
BODY_SM = 13
CAPTION_SIZE = 11
CARD_VALUE = 30
CARD_VALUE_SM = 15
INPUT_SIZE = 15

BUTTON_H = 46
MIN_TOUCH = 44

# ---- motion ---------------------------------------------------------------
# One switch for every animation. Keep transitions short: a fade in and out
# should never make the app feel slower than it is.
ANIMATION_MS = 160

# Set from the user's saved "reduce motion" preference at startup. Flet has
# no access to the OS setting, so the app carries its own switch and every
# animation asks `duration()` before it runs.
_REDUCE_MOTION = False


def set_reduce_motion(value: bool) -> None:
    global _REDUCE_MOTION
    _REDUCE_MOTION = bool(value)


def reduce_motion() -> bool:
    return _REDUCE_MOTION


def duration(ms: int = ANIMATION_MS) -> int:
    """Milliseconds as Flet expects them; 0 disables the animation."""

    return 0 if _REDUCE_MOTION else ms


def money(amount, currency: str = "ZAR") -> str:
    """Format an API money string ("18450.0") as "R 18 450".

    Groups thousands with a thin-looking space, as in the wireframes.
    """

    try:
        value = float(amount or 0)
    except (TypeError, ValueError):
        value = 0.0

    cents = round(value, 2)
    whole = int(abs(cents))
    fractional = round((abs(cents) - whole) * 100)

    grouped = f"{whole:,}".replace(",", " ")
    text = f"{grouped}.{fractional:02d}" if fractional else grouped
    sign = "-" if cents < 0 else ""
    return f"{sign}R {text}" if currency == "ZAR" else f"{sign}{text} {currency}"


def short_date(iso_date) -> str:
    """'2026-06-28' -> '28 Jun' (the timeline rows omit the year)."""

    if not iso_date:
        return ""
    from datetime import date

    try:
        d = date.fromisoformat(str(iso_date)[:10])
    except ValueError:
        return str(iso_date)
    return f"{d.day:02d} {d:%b}"


def month_label(month: str) -> str:
    """'2026-06' -> 'JUNE 2026'."""

    try:
        year, mon = month.split("-")
        from datetime import date

        name = date(int(year), int(mon), 1).strftime("%B")
        return f"{name} {year}".upper()
    except (ValueError, AttributeError):
        return str(month or "")


def month_nav(month: str, delta: int) -> str:
    """Step a 'YYYY-MM' label by whole months."""

    year, mon = (int(p) for p in month.split("-"))
    index = year * 12 + (mon - 1) + delta
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def current_month() -> str:
    from datetime import date

    return date.today().strftime("%Y-%m")


def format_date(iso_date) -> str:
    """'2026-06-28' -> '28 Jun 2026'."""

    if not iso_date:
        return "Not set"
    from datetime import date

    try:
        d = date.fromisoformat(str(iso_date)[:10])
    except ValueError:
        return str(iso_date)
    return f"{d.day:02d} {d:%b %Y}"


def to_amount(raw) -> str | None:
    """'R 18 450' / '18 450,50' / '18450' -> '18450.00' (None when blank).

    Raises ValueError for anything that is not a number, so a typo shows up
    next to the field instead of coming back as a 422.
    """

    from decimal import Decimal, InvalidOperation

    if raw is None:
        return None
    cleaned = (
        str(raw)
        .replace("R", "")
        .replace(" ", "")
        .replace(" ", "")
        .replace(",", ".")
        .strip()
    )
    if not cleaned:
        return None
    if cleaned.count(".") > 1:
        raise ValueError(f"“{raw}” is not a valid amount.")
    try:
        return f"{Decimal(cleaned):.2f}"
    except InvalidOperation:
        raise ValueError(f"“{raw}” is not a valid amount.") from None


def balance_series(events) -> list[tuple[str, float]]:
    """(label, balance) pairs from a cash-flow timeline, for the overview
    sparkline. Skips rows without a balance; never invents a point."""

    series: list[tuple[str, float]] = []
    for event in events or []:
        try:
            value = float(event.get("balance"))
        except (TypeError, ValueError):
            continue
        label = event.get("date") or event.get("label") or ""
        series.append((str(label)[:10], value))
    return series


def shown_amount(value) -> str:
    """Render an API money string in a text field without '.0' noise."""

    if value in (None, ""):
        return ""
    return to_amount(value) or ""


def style_input(control: ft.Control) -> ft.Control:
    """Apply the shared outlined-input look to a TextField / Dropdown."""

    control.text_size = INPUT_SIZE
    control.border = ft.OutlineInputBorder(
        border_radius=ft.BorderRadius.all(RADIUS),
        side=ft.BorderSide(1, BORDER),
    )
    control.content_padding = ft.Padding.symmetric(
        horizontal=SPACE_M, vertical=SPACE_L - 2
    )
    return control


def caption(text: str) -> ft.Text:
    return ft.Text(text, size=CAPTION_SIZE, weight=ft.FontWeight.W_600, color=MUTED)


def helper(text: str) -> ft.Text:
    return ft.Text(text, size=BODY_SM, color=MUTED)


def note(text: str, bg: str = NOTE_BG) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=BODY_SM, color=INK),
        bgcolor=bg,
        padding=ft.Padding.all(SPACE_M),
        border=ft.Border(
            left=ft.BorderSide(3, INK if bg == NOTE_BG else ACCENT_MOOD)
        ),
    )


def primary_button(label: str, on_click, expand: bool = False, disabled=False):
    return ft.FilledButton(
        content=label,
        bgcolor=INK,
        color=BG,
        height=BUTTON_H,
        expand=expand,
        disabled=disabled,
        on_click=on_click,
    )


def secondary_button(label: str, on_click, expand: bool = False):
    return ft.Button(
        content=label,
        color=INK,
        height=BUTTON_H,
        expand=expand,
        style=ft.ButtonStyle(
            bgcolor=SURFACE,
            side=ft.BorderSide(1, BORDER),
            shape=ft.RoundedRectangleBorder(radius=RADIUS),
        ),
        on_click=on_click,
    )


def text_button(label: str, on_click):
    return ft.TextButton(
        content=ft.Text(label, size=BODY_SM, color=INK),
        style=ft.ButtonStyle(
            overlay_color=ft.Colors.TRANSPARENT,
            padding=ft.Padding.symmetric(horizontal=0, vertical=SPACE_S),
        ),
        on_click=on_click,
    )


def logo() -> ft.Row:
    return ft.Row(
        spacing=SPACE_S - 2,
        controls=[
            ft.Container(
                content=ft.Text("FS", size=10, weight=ft.FontWeight.BOLD, color=BG),
                bgcolor=INK,
                border_radius=3,
                width=18,
                height=18,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Text(
                "FlowShelter", size=BODY, weight=ft.FontWeight.W_600, color=INK
            ),
        ],
    )
