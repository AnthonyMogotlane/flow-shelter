"""Reusable pieces of the onboarding chrome and the tab screens.

Everything visual comes from `theme.py`: no raw hex colour or magic font
size should appear in a screen module.
"""

import asyncio
from datetime import date, datetime

import flet as ft

from theme import (
    ACCENT_MOOD,
    BG,
    BODY,
    BODY_SM,
    BORDER,
    BUTTON_H,
    CAPTION_SIZE,
    CARD_VALUE,
    ERROR,
    HEADING,
    INK,
    INPUT_SIZE,
    MUTED,
    NOTE_BG,
    PAD,
    PAGE_PAD,
    RADIUS,
    RADIUS_PILL,
    RADIUS_SM,
    SPACE_L,
    SPACE_M,
    SPACE_S,
    SPACE_XL,
    SPACE_XS,
    SUBHEAD,
    SUCCESS,
    SURFACE,
    TITLE,
    TITLE_SM,
    WARN_BG,
    caption,
    logo,
    reduce_motion,
    style_input,
)


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
def chrome_theme() -> ft.Theme:
    """App theme for the shared tab chrome.

    Only values verified against this Flet SDK are set. Its
    `NavigationBarTheme` has no icon entry at all, and `NavigationBar` has no
    label or icon colour props, so the bottom-bar label/icon colours come
    from Material's own scheme.
    """

    return ft.Theme(
        navigation_bar_theme=ft.NavigationBarTheme(
            label_text_style={
                ft.ControlState.DEFAULT: ft.TextStyle(
                    size=CAPTION_SIZE - 1, color=MUTED
                ),
                ft.ControlState.SELECTED: ft.TextStyle(
                    size=CAPTION_SIZE - 1, weight=ft.FontWeight.W_600, color=INK
                ),
            },
        )
    )


# ---------------------------------------------------------------------------
# Form controls
# ---------------------------------------------------------------------------
class DateField:
    """A read-only text field that opens a DatePicker dialog.

    Exposes `.value` as an ISO date string (`YYYY-MM-DD`) or None.
    """

    def __init__(self, page: ft.Page, label: str, on_change=None):
        self.page = page
        self._selected: date | None = None
        self._on_change = on_change
        self.field = style_input(
            ft.TextField(
                label=label,
                hint_text="dd/mm/yyyy",
                read_only=True,
                on_click=self._open,
                suffix_icon=ft.Icon(ft.Icons.CALENDAR_TODAY, size=18, color=MUTED),
            )
        )
        self.picker = ft.DatePicker(
            first_date=date.today().replace(year=date.today().year - 1),
            last_date=date.today().replace(year=date.today().year + 5),
            on_change=self._picked,
        )

    @property
    def value(self) -> str | None:
        return self._selected.isoformat() if self._selected else None

    @value.setter
    def value(self, iso):
        if not iso:
            self._selected = None
            self.field.value = ""
            return
        try:
            self._selected = date.fromisoformat(str(iso)[:10])
            self.field.value = self._selected.strftime("%d/%m/%Y")
        except ValueError:
            self._selected = None
            self.field.value = ""

    def _open(self, e=None):
        self.page.show_dialog(self.picker)

    def _picked(self, e):
        raw = self.picker.value
        if isinstance(raw, str):
            try:
                raw = datetime.fromisoformat(raw)
            except ValueError:
                return
        if raw is not None:
            self._selected = raw.date() if hasattr(raw, "date") else raw
            self.field.value = self._selected.strftime("%d/%m/%Y")
        else:
            self._selected = None
            self.field.value = ""
        self.page.pop_dialog()
        self.page.update()
        if self._on_change is not None:
            self._on_change(self.value)


def field_label(text: str) -> ft.Text:
    return ft.Text(text, size=BODY_SM - 1, weight=ft.FontWeight.W_600, color=INK)


def labeled(text: str, control: ft.Control) -> ft.Column:
    return ft.Column(spacing=SPACE_S - 2, controls=[field_label(text), control])


def error_text() -> ft.Text:
    """Placeholder for an inline form error; pair with `set_error`.

    `set_error` fills and shows it, so the message lands directly above the
    buttons that produced it.
    """

    return ft.Text(
        size=BODY_SM,
        color=ERROR,
        weight=ft.FontWeight.W_500,
        visible=False,
    )


def set_error(control: ft.Text, message: str | None, page: ft.Page) -> None:
    control.value = message or ""
    control.visible = bool(message)
    page.update()


def submit_button(label: str, on_click, expand: bool = True) -> ft.FilledButton:
    """Primary button that swaps its label for a spinner while a request runs.

    Pair with `set_busy(button, True/False)`; the label is kept on `data` so
    the same control can be used again after a failure.
    """

    button = ft.FilledButton(
        content=ft.Text(label),
        bgcolor=INK,
        color=BG,
        height=BUTTON_H,
        expand=expand,
        on_click=on_click,
    )
    button.data = {"label": label}  # type: ignore[attr-defined]
    return button


def set_busy(button: ft.Control, busy: bool) -> None:
    """Swap a `submit_button`'s label for a spinner, and back again."""

    label = (getattr(button, "data", None) or {}).get("label", "")
    if busy:
        button.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.ProgressRing(width=16, height=16, stroke_width=2, color=BG),
            ],
        )
    else:
        button.content = ft.Text(label)
    button.disabled = busy


def submit_row(on_cancel, submit: ft.Control) -> ft.Row:
    """Cancel on the left, the busy-aware primary action on the right."""

    return ft.Row(
        spacing=SPACE_M - 2,
        controls=[
            ft.Column(
                expand=True,
                controls=[
                    ft.Button(
                        content="Cancel",
                        color=INK,
                        height=BUTTON_H,
                        expand=True,
                        style=ft.ButtonStyle(
                            bgcolor=SURFACE,
                            side=ft.BorderSide(1, BORDER),
                            shape=ft.RoundedRectangleBorder(radius=RADIUS),
                        ),
                        on_click=on_cancel,
                    )
                ],
            ),
            ft.Column(expand=True, controls=[submit]),
        ],
    )


# ---------------------------------------------------------------------------
# Onboarding chrome
# ---------------------------------------------------------------------------
def top_bar(on_save_exit=None, right_text: str | None = None) -> ft.Row:
    """Logo on the left; either a title or 'Save & exit' on the right."""

    if on_save_exit is not None:
        right: ft.Control = ft.TextButton(
            content=ft.Text("Save & exit", size=BODY_SM, color=INK),
            style=ft.ButtonStyle(
                overlay_color=ft.Colors.TRANSPARENT,
                padding=ft.Padding.symmetric(horizontal=0),
            ),
            on_click=on_save_exit,
        )
    else:
        right = ft.Text(
            right_text or "",
            size=BODY_SM,
            weight=ft.FontWeight.W_600,
            color=INK,
        )
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[logo(), right],
    )


def progress_header(step: int, total: int = 5) -> ft.Control:
    """'Set up your plan · Step N of M' + progress bar."""

    return ft.Column(
        spacing=SPACE_M - 2,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Set up your plan", size=BODY_SM, color=INK),
                    ft.Text(
                        f"Step {step} of {total}",
                        size=BODY_SM,
                        weight=ft.FontWeight.W_600,
                        color=INK,
                    ),
                ],
            ),
            ft.ProgressBar(
                value=step / total,
                color=INK,
                bgcolor=BORDER,
                bar_height=4,
                border_radius=2,
            ),
        ],
    )


def page_title(title: str, subtitle: str | None = None) -> ft.Column:
    """The standard page heading: big title plus an optional supporting line."""

    controls: list[ft.Control] = [
        ft.Text(title, size=TITLE, weight=ft.FontWeight.W_700, color=INK)
    ]
    if subtitle:
        controls.append(ft.Text(subtitle, size=BODY, color=MUTED))
    return ft.Column(spacing=SPACE_S - 2, controls=controls)


# Onboarding predates `page_title`; keep its older name as an alias so both
# styles resolve from one place.
section_title = page_title


def step_title(title: str, subtitle: str | None = None) -> ft.Column:
    """Onboarding's slightly smaller heading, same subtitle treatment."""

    controls: list[ft.Control] = [
        ft.Text(title, size=TITLE_SM, weight=ft.FontWeight.W_700, color=INK)
    ]
    if subtitle:
        controls.append(ft.Text(subtitle, size=BODY, color=MUTED))
    return ft.Column(spacing=SPACE_S, controls=controls)


def card(content: ft.Control, padding: int = SPACE_L) -> ft.Container:
    return ft.Container(
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=RADIUS,
        padding=padding,
        content=content,
    )


def tappable(control: ft.Container, on_click) -> ft.Container:
    """Make a card an obvious target: a press ripple and pointer cursor.

    Ripples are Material's own pressed feedback, so this keeps the card in
    step with buttons; reduced motion turns them off.
    """

    control.on_click = on_click
    control.ink = not reduce_motion()
    return control


def onboarding_view(
    page: ft.Page,
    step: int,
    title: str,
    subtitle: str | None,
    body: list[ft.Control],
    footer: ft.Control,
    on_save_exit=None,
    scroll: bool = False,
) -> ft.View:
    """Common onboarding layout: top bar, header card with title, body, footer."""

    steps = ft.Column(
        spacing=SPACE_L + 2,
        controls=[
            progress_header(step),
            step_title(title, subtitle),
            *body,
        ],
    )

    page_content = ft.Column(
        spacing=SPACE_XS,
        controls=[steps] + ([footer] if footer is not None else []),
    )

    return ft.View(
        route="/",
        bgcolor=BG,
        padding=ft.Padding.symmetric(horizontal=SPACE_M, vertical=SPACE_S),
        controls=[
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=SPACE_S),
                content=top_bar(on_save_exit=on_save_exit),
            ),
            card(page_content, padding=PAD),
            ft.Container(height=SPACE_S),
        ],
        scroll=ft.ScrollMode.AUTO if scroll else ft.ScrollMode.ADAPTIVE,
    )


# ---------------------------------------------------------------------------
# Tab chrome (Overview, Cash flow, Transactions, Goals)
# ---------------------------------------------------------------------------
TAB_ITEMS = [
    ("overview", "Overview", ft.Icons.HOME_OUTLINED),
    ("cashflow", "Cash flow", ft.Icons.INSIGHTS_OUTLINED),
    ("transactions", "Transactions", ft.Icons.SWAP_VERT_OUTLINED),
    ("goals", "Goals", ft.Icons.FLAG_OUTLINED),
]

# Each tab paints its own icon when active, matching the wireframes.
TAB_ACTIVE_ICONS = {
    "overview": ft.Icons.HOME,
    "cashflow": ft.Icons.INSIGHTS,
    "transactions": ft.Icons.SWAP_VERT,
    "goals": ft.Icons.FLAG,
}

TAB_KEYS = [key for key, _, _ in TAB_ITEMS]


def initials(overview: dict | None) -> str:
    user = (overview or {}).get("user") or {}
    name = (user.get("name") or "").strip()
    parts = [p for p in name.split() if p]
    if not parts:
        return "?"
    return "".join(p[0].upper() for p in parts[:2])


def tab_top_bar(title: str, app, theme_icon=None, on_back=None) -> ft.Row:
    """'FLOWSHELTER / <title>' on the left; theme, avatar (and back) right."""

    left: list[ft.Control] = []
    if on_back is not None:
        left.append(
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_size=20,
                icon_color=INK,
                tooltip="Back",
                on_click=on_back,
            )
        )
    left.append(
        ft.Column(
            spacing=0,
            controls=[
                ft.Text("FLOWSHELTER", size=CAPTION_SIZE - 2, color=MUTED),
                ft.Text(
                    title, size=SUBHEAD, weight=ft.FontWeight.W_600, color=INK
                ),
            ],
        )
    )

    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=SPACE_XS,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=left,
            ),
            ft.Row(
                spacing=SPACE_M,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    theme_icon
                    or ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, size=18, color=INK),
                    ft.Container(
                        width=30,
                        height=30,
                        bgcolor=BORDER,
                        border_radius=15,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(
                            initials(app.overview), size=CAPTION_SIZE, color=INK
                        ),
                    ),
                ],
            ),
        ],
    )


def bottom_nav(active: str, on_select) -> ft.Control:
    """The four destinations, on Material's `NavigationBar`.

    Using the built-in bar keeps Material's active indicator, focus order
    and pinned layout instead of a hand-rolled row of containers.
    """

    index = TAB_KEYS.index(active) if active in TAB_KEYS else 0
    return ft.NavigationBar(
        selected_index=index,
        on_change=lambda e: on_select(TAB_KEYS[int(e.control.selected_index)]),
        bgcolor=SURFACE,
        indicator_color=BORDER,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        height=64,
        destinations=[
            ft.NavigationBarDestination(
                icon=icon,
                selected_icon=TAB_ACTIVE_ICONS[key],
                label=label,
            )
            for key, label, icon in TAB_ITEMS
        ],
    )


def skeleton_block(
    height: float, radius: int = RADIUS_SM, width: float | None = None
) -> ft.Container:
    """One placeholder bar; shimmers unless the user reduced motion."""

    body = ft.Container(height=height, width=width)
    if reduce_motion():
        # A still bar: same shape and colour, no movement.
        return ft.Container(
            height=height,
            width=width,
            border_radius=radius,
            bgcolor=NOTE_BG,
        )
    return ft.Container(
        height=height,
        width=width,
        border_radius=radius,
        bgcolor=NOTE_BG,
        content=ft.Shimmer(
            base_color=NOTE_BG,
            highlight_color=SURFACE,
            content=body,
        ),
    )


# Falling widths keep a placeholder card from looking like a solid slab.
_LINE_WIDTHS = (1.0, 0.72, 0.5)


def skeleton_card(lines: int = 3, title: bool = True) -> ft.Container:
    """A card-shaped placeholder for content that is still loading.

    The first line stands in for a card's headline figure when `title`, and
    each line after it narrows, so the block reads as text rather than bars.
    """

    blocks: list[ft.Control] = []
    for index in range(max(lines, 1)):
        if title and index == 0:
            blocks.append(skeleton_block(CARD_VALUE - 6, width=150))
            continue
        share = _LINE_WIDTHS[min(index, len(_LINE_WIDTHS) - 1)]
        blocks.append(skeleton_block(BODY_SM, width=220 * share))
    return card(ft.Column(spacing=SPACE_M, controls=blocks))


def skeleton_page(title_width: int = 190, cards: int = 3) -> ft.Column:
    """A whole tab body while it first loads: heading, subtitle, cards.

    Mirrors the real layout (title, supporting line, stacked cards) so the
    content slots into place without a jump when the data arrives.
    """

    return ft.Column(
        spacing=SPACE_L,
        controls=[
            ft.Column(
                spacing=SPACE_S - 2,
                controls=[
                    skeleton_block(TITLE - 6, width=title_width),
                    skeleton_block(BODY, width=int(title_width * 1.6)),
                ],
            ),
            *[skeleton_card(3 if index == 0 else 2) for index in range(cards)],
        ],
    )


def tab_view(
    title: str,
    app,
    body: ft.Control,
    active: str,
    theme_icon=None,
    on_back=None,
    loading: bool = False,
    route: str | None = None,
    show_nav: bool = True,
) -> ft.View:
    """Top bar, a body that scrolls on its own, and the bottom nav.

    The nav and top bar sit outside the scroll area, so the bottom bar stays
    put however long the content is. While `loading` is set the body shows a
    skeleton of the screen's shape; the screen drives it through the
    `body_slot` / `loading_state` attributes attached to the returned view
    (see `LoadingState`). Forms opened over a tab (`on_back` set) hide the
    nav; the tab underneath paints the same surface colour.
    """

    page = app.page
    route = route or f"/{active}"
    if on_back is not None:
        show_nav = False
    skeleton = skeleton_body()
    body_slot = ft.Column(
        expand=True,
        spacing=0,
        visible=not loading,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Container(
                padding=ft.Padding.only(bottom=SPACE_S),
                content=body,
            )
        ],
    )
    view = ft.View(
        route=route,
        bgcolor=BG,
        padding=0,
        controls=[
            ft.Container(
                padding=ft.Padding.symmetric(
                    horizontal=PAGE_PAD, vertical=SPACE_M - 2
                ),
                content=tab_top_bar(title, app, theme_icon, on_back),
            ),
            ft.Column(
                expand=True,
                spacing=0,
                controls=[body_slot, skeleton],
            ),
            ft.Container(
                visible=show_nav,
                content=bottom_nav(
                    active, lambda key: page.run_task(app.open_tab, key)
                ),
            ),
        ],
        # The view itself never scrolls, so the nav cannot be pushed offscreen.
        scroll=ft.ScrollMode.HIDDEN,
    )
    # Screens reach in through these to drive their own loading state; Flet
    # controls accept arbitrary attributes.
    view.body_slot = body_slot  # type: ignore[attr-defined]
    view.loading_state = LoadingState(page, skeleton)  # type: ignore[attr-defined]
    if loading:
        # Built while there is no content yet: show the placeholder straight
        # away (no delay) so the first frame is never blank.
        skeleton.visible = True
    return view


# A load that finishes sooner than this never shows a placeholder: a flash of
# skeleton on a fast local response reads as a glitch, not as feedback.
SKELETON_DELAY_MS = 150


def refresh_indicator() -> ft.ProgressBar:
    """A hairline bar shown while content is re-fetched behind the scenes.

    Filters and month arrows keep the current figures on screen; this says
    they are being updated without blanking or shifting the layout.
    """

    return ft.ProgressBar(
        value=None,
        color=INK,
        bgcolor=BORDER,
        bar_height=2,
        border_radius=1,
        visible=False,
    )


def skeleton_body() -> ft.Container:
    """The tab body while it first loads, matching the screen's real layout.

    Starts hidden; `LoadingState` reveals it once a load has taken a moment.
    """

    return ft.Container(
        expand=True,
        visible=False,
        alignment=ft.Alignment.TOP_CENTER,
        padding=ft.Padding.symmetric(horizontal=PAGE_PAD, vertical=SPACE_M),
        content=skeleton_page(),
    )


class LoadingState:
    """Tracks one screen load and reveals its skeleton after `delay_ms`.

    `start()` begins the delay; if the load finishes first nothing is ever
    shown, so only genuinely slow loads get a placeholder. Pass
    `immediate=True` when the screen has no content to keep on screen (a
    first open), which skips the delay. `finish()` hides the skeleton.
    """

    def __init__(self, page: ft.Page, skeleton: ft.Container,
                 delay_ms: int = SKELETON_DELAY_MS):
        self.page = page
        self.skeleton = skeleton
        self.delay_ms = delay_ms
        self._token = 0

    def start(self, immediate: bool = False) -> int:
        self._token += 1
        self.skeleton.visible = immediate
        if immediate:
            self.page.update(self.skeleton)
        else:
            self.page.run_task(self._reveal, self._token)
        return self._token

    async def _reveal(self, token: int):
        await asyncio.sleep(self.delay_ms / 1000)
        if token != self._token:
            return  # a newer load started, or this one finished
        self.skeleton.visible = True
        self.page.update(self.skeleton)

    def finish(self) -> None:
        """Stop the delay and hide the skeleton."""

        self._token += 1
        self.skeleton.visible = False


def padded(control: ft.Control) -> ft.Container:
    """The standard body inset inside a tab screen."""

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=PAGE_PAD, vertical=SPACE_M),
        content=control,
    )


# ---------------------------------------------------------------------------
# Content pieces
# ---------------------------------------------------------------------------
def segmented(options: list[tuple[str, str]], value: str, on_select) -> ft.Container:
    """A small pill group, e.g. 'Until next payment | Monthly' or
    'All | Income | Expenses'. `options` is (key, label) pairs."""

    segments = []
    for key, label in options:
        selected = key == value
        segments.append(
            ft.Container(
                bgcolor=INK if selected else SURFACE,
                border_radius=RADIUS_SM,
                # 28px of text plus the padding keeps the tap target ~44px.
                padding=ft.Padding.symmetric(
                    horizontal=SPACE_M + 2, vertical=SPACE_M - 2
                ),
                content=ft.Text(
                    label,
                    size=BODY_SM,
                    weight=ft.FontWeight.W_600 if selected else None,
                    color=BG if selected else INK,
                ),
                on_click=None if selected else (lambda e, k=key: on_select(k)),
                # A tooltip gives the pill a hover/screen-reader name; the
                # selected segment has no click handler, so assistive tech
                # reads it as the current choice rather than an action.
                tooltip=label,
            )
        )
    return ft.Container(
        border=ft.Border.all(1, BORDER),
        border_radius=RADIUS,
        padding=3,
        content=ft.Row(spacing=0, controls=segments),
    )


def pill(label: str, bg: str = NOTE_BG, fg: str | None = None) -> ft.Container:
    """A small rounded label. Pass `fg` when the background is dark."""

    return ft.Container(
        bgcolor=bg,
        border_radius=RADIUS_PILL,
        padding=ft.Padding.symmetric(horizontal=SPACE_S, vertical=3),
        content=ft.Text(label, size=CAPTION_SIZE, color=fg or INK),
    )


def stat_card(
    label: str,
    value: str,
    detail: str | None = None,
    size: int = CARD_VALUE,
) -> ft.Container:
    """A labelled money figure. `size` lets tight rows use the small scale."""

    controls: list[ft.Control] = [
        caption(label.upper()),
        ft.Text(value, size=size, weight=ft.FontWeight.W_700, color=INK),
    ]
    if detail:
        controls.append(ft.Text(detail, size=BODY_SM, color=MUTED))
    return card(
        ft.Column(
            spacing=SPACE_S - 2,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=controls,
        )
    )


def figure(label: str, value: str) -> ft.Column:
    """A small label-over-value pair used inside goal and summary cards."""

    return ft.Column(
        spacing=2,
        controls=[
            caption(label.upper()),
            ft.Text(value, size=INPUT_SIZE, weight=ft.FontWeight.W_600, color=INK),
        ],
    )


def heading(text: str) -> ft.Text:
    return ft.Text(text, size=HEADING, weight=ft.FontWeight.W_700, color=INK)


def detail_text(text: str) -> ft.Text:
    return ft.Text(text, size=BODY_SM, color=MUTED)


def empty_state(
    title: str,
    message: str,
    icon: str = ft.Icons.INBOX_OUTLINED,
    action: ft.Control | None = None,
) -> ft.Container:
    """A quiet card explaining why a list is empty, with an optional action."""

    controls: list[ft.Control] = [
        ft.Icon(icon, size=28, color=MUTED),
        ft.Text(
            title,
            size=SUBHEAD,
            weight=ft.FontWeight.W_600,
            color=INK,
            text_align=ft.TextAlign.CENTER,
        ),
        ft.Text(message, size=BODY_SM, color=MUTED, text_align=ft.TextAlign.CENTER),
    ]
    if action is not None:
        controls.append(ft.Container(height=SPACE_XS))
        controls.append(action)
    return card(
        ft.Column(
            spacing=SPACE_S,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        ),
        padding=SPACE_XL,
    )


def error_card(message: str, on_retry=None) -> ft.Container:
    """An inline error with an optional 'Try again' action."""

    controls: list[ft.Control] = [
        ft.Row(
            spacing=SPACE_S,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=18, color=ERROR),
                ft.Text(message, size=BODY, color=INK, expand=True),
            ],
        )
    ]
    if on_retry is not None:
        controls.append(
            ft.TextButton(
                content=ft.Text("Try again", size=BODY_SM, color=INK),
                style=ft.ButtonStyle(
                    overlay_color=ft.Colors.TRANSPARENT,
                    padding=ft.Padding.symmetric(
                        horizontal=0, vertical=SPACE_S
                    ),
                ),
                on_click=on_retry,
            )
        )
    return card(ft.Column(spacing=SPACE_XS, controls=controls))


def snack(page: ft.Page, message: str, kind: str = "success") -> None:
    """Show a short, factual confirmation at the bottom of the screen."""

    bgcolor = {"success": SUCCESS, "error": ERROR, "info": INK}.get(kind, INK)
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(message, size=BODY_SM, color=SURFACE),
            bgcolor=bgcolor,
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=2500,
        )
    )


def alert_banner(alert: dict, on_review=None) -> ft.Container:
    """A dashboard alert. Warns in the accent colour, never blames the user."""

    severity = alert.get("severity") or alert.get("level") or "info"
    serious = severity in ("warning", "warn", "overdue")
    controls: list[ft.Control] = [
        ft.Column(
            spacing=SPACE_XS,
            expand=True,
            controls=[
                ft.Text(
                    alert.get("message") or "Something needs your attention.",
                    size=BODY,
                    weight=ft.FontWeight.W_600,
                    color=INK,
                ),
            ],
        )
    ]
    if on_review is not None:
        controls.append(
            ft.TextButton(
                content=ft.Text("Review", size=BODY_SM, color=INK),
                style=ft.ButtonStyle(
                    overlay_color=ft.Colors.TRANSPARENT,
                    padding=ft.Padding.symmetric(
                        horizontal=SPACE_S, vertical=SPACE_S
                    ),
                ),
                on_click=on_review,
            )
        )
    return ft.Container(
        bgcolor=WARN_BG if serious else NOTE_BG,
        border_radius=RADIUS,
        padding=ft.Padding.symmetric(horizontal=SPACE_M, vertical=SPACE_M),
        border=ft.Border(left=ft.BorderSide(3, ACCENT_MOOD if serious else BORDER)),
        content=ft.Row(
            spacing=SPACE_S,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=controls,
        ),
    )


def nav_footer(on_back=None, on_continue=None, continue_label="Continue",
               back_label="Back", skip_label: str | None = None,
               submit: ft.Control | None = None) -> ft.Row:
    """Bottom row: optional secondary button on the left, primary on the right.

    Pass `submit` (a `submit_button`) instead of `on_continue` when the
    primary action runs a request, so it can show a spinner while saving.
    """

    left: list[ft.Control] = []
    if skip_label is not None:
        left.append(
            ft.TextButton(
                content=ft.Text(skip_label, size=BODY_SM, color=INK),
                style=ft.ButtonStyle(
                    overlay_color=ft.Colors.TRANSPARENT,
                    padding=ft.Padding.symmetric(horizontal=0),
                ),
                on_click=on_back,
            )
        )
    elif on_back is not None:
        left.append(
            ft.Column(
                expand=True,
                controls=[
                    ft.Button(
                        content=back_label,
                        color=INK,
                        height=BUTTON_H,
                        style=ft.ButtonStyle(
                            bgcolor=SURFACE,
                            side=ft.BorderSide(1, BORDER),
                            shape=ft.RoundedRectangleBorder(radius=RADIUS),
                        ),
                        on_click=on_back,
                    )
                ],
            )
        )

    primary = submit or ft.FilledButton(
        content=continue_label,
        bgcolor=INK,
        color=BG,
        height=BUTTON_H,
        expand=True,
        on_click=on_continue,
    )
    return ft.Row(
        spacing=SPACE_M - 2,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=left + [primary],
    )
