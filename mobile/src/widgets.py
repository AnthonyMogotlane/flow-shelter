"""Reusable pieces of the onboarding chrome and the tab screens.

Everything visual comes from `theme.py`: no raw hex colour or magic font
size should appear in a screen module.
"""

from i18n import t
from i18n import translated_server_text

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
    CARD_SHADOW,
    ERROR,
    HEADING,
    INK,
    INPUT_SIZE,
    MUTED,
    NOTE_BG,
    MINT,
    PRIMARY,
    PRIMARY_DARK,
    ON_PRIMARY,
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
    duration,
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
        color_scheme=ft.ColorScheme(
            primary=PRIMARY, on_primary=SURFACE, surface=SURFACE,
            on_surface=INK, error=ERROR, outline=BORDER,
        ),
        navigation_bar_theme=ft.NavigationBarTheme(
            label_text_style={
                ft.ControlState.DEFAULT: ft.TextStyle(
                    size=CAPTION_SIZE - 1, color=MUTED
                ),
                ft.ControlState.SELECTED: ft.TextStyle(
                    size=CAPTION_SIZE - 1, weight=ft.FontWeight.W_600, color=INK
                ),
            },
        ),
        page_transitions=ft.PageTransitionsTheme(
            android=(
                ft.PageTransitionTheme.NONE
                if reduce_motion()
                else ft.PageTransitionTheme.FADE_UPWARDS
            ),
            ios=(
                ft.PageTransitionTheme.NONE
                if reduce_motion()
                else ft.PageTransitionTheme.CUPERTINO
            ),
            linux=(
                ft.PageTransitionTheme.NONE
                if reduce_motion()
                else ft.PageTransitionTheme.ZOOM
            ),
            macos=(
                ft.PageTransitionTheme.NONE
                if reduce_motion()
                else ft.PageTransitionTheme.ZOOM
            ),
            windows=(
                ft.PageTransitionTheme.NONE
                if reduce_motion()
                else ft.PageTransitionTheme.ZOOM
            ),
        ),
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


def validate_fields(page, rules) -> bool:
    """Render errors next to their fields, clearing previous validation."""
    valid = True
    for control, message in rules:
        control.error_text = message
        valid = valid and not message
    page.update()
    return valid


def submit_button(label: str, on_click, expand: bool = True) -> ft.FilledButton:
    """Primary button that swaps its label for a spinner while a request runs.

    Pair with `set_busy(button, True/False)`; the label is kept on `data` so
    the same control can be used again after a failure.
    """

    button = ft.FilledButton(
        content=ft.Text(label),
        bgcolor=PRIMARY,
        color=BG,
        height=BUTTON_H,
        expand=expand,
        style=ft.ButtonStyle(
            animation_duration=duration(),
            text_style=ft.TextStyle(size=BODY, weight=ft.FontWeight.W_600),
            shape=ft.RoundedRectangleBorder(radius=RADIUS),
        ),
        on_click=on_click,
    )
    button.data = {"label": label}  # type: ignore[attr-defined]
    return button


def set_busy(button: ft.Control, busy: bool, busy_label: str = t('Saving')) -> None:
    """Swap a `submit_button`'s label for a spinner, and back again."""

    label = (getattr(button, "data", None) or {}).get("label", "")
    if busy:
        button.content = ft.Semantics(
            label=busy_label,
            live_region=True,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.ProgressRing(width=16, height=16, stroke_width=2, color=BG),
                ],
            ),
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
            content=ft.Text(t('Save & exit'), size=BODY_SM, color=INK),
            style=ft.ButtonStyle(
                overlay_color={ft.ControlState.FOCUSED: BORDER,
                               ft.ControlState.PRESSED: NOTE_BG},
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
                    ft.Text(t('Set up your plan'), size=BODY_SM, color=INK),
                    ft.Text(
                        t('Step {v0} of {v1}', v0=step, v1=total),
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
        shadow=ft.BoxShadow(blur_radius=16, spread_radius=0,
                            color=CARD_SHADOW, offset=ft.Offset(0, 3)),
        padding=padding,
        content=content,
    )


def tappable(control: ft.Container, on_click, label: str) -> ft.Semantics:
    """Give a clickable card touch feedback and an accessible button label.

    Ripples are Material's own pressed feedback, so this keeps the card in
    step with buttons; reduced motion turns them off.
    """

    control.on_click = on_click
    control.ink = not reduce_motion()
    return ft.Semantics(
        content=control,
        label=label,
        button=True,
        focusable=True,
        on_tap=on_click,
    )


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
    ("overview", t('Overview'), ft.Icons.HOME_OUTLINED),
    ("cashflow", t('Cash flow'), ft.Icons.INSIGHTS_OUTLINED),
    ("transactions", t('Transactions'), ft.Icons.SWAP_VERT_OUTLINED),
    ("goals", t('Goals'), ft.Icons.FLAG_OUTLINED),
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
        return (user.get("email") or "")[:1].upper()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][0].upper()


def account_user(app) -> dict:
    return getattr(app, "profile_user", {}) or (app.overview or {}).get("user") or {}


class ProfileAvatar(ft.TextButton):
    """Update initials when account data arrives after the header is built."""

    def __init__(self, app):
        self.app = app
        super().__init__(
            width=44, height=44, tooltip=t('Open profile'),
            style=ft.ButtonStyle(padding=ft.Padding.all(0),
                                 shape=ft.CircleBorder()),
            on_click=lambda e: app.page.run_task(app.open_profile),
            content=ft.Container(
                width=36, height=36, bgcolor=MINT, border_radius=18,
                alignment=ft.Alignment.CENTER,
            ),
        )
        self.before_update()

    def before_update(self):
        user = account_user(self.app)
        text = initials({"user": user})
        self.content.content = (
            ft.Text(text, size=BODY_SM, weight=ft.FontWeight.W_600, color=PRIMARY)
            if text else ft.Icon(ft.Icons.PERSON_OUTLINE, size=20, color=PRIMARY)
        )


def tab_top_bar(title: str, app, theme_icon=None, on_back=None) -> ft.Row:
    """Brand on tab screens; contextual title and Back on secondary screens."""

    left: list[ft.Control] = []
    if on_back is not None:
        left.append(
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_size=20,
                icon_color=INK,
                tooltip=t('Back'),
                on_click=on_back,
            )
        )
    left.append(
        logo() if on_back is None else ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Text(t('FLOWSHELTER'), size=CAPTION_SIZE - 2, color=MUTED),
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
                expand=True,
                spacing=SPACE_XS,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=left,
            ),
            ft.Row(
                spacing=SPACE_M,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=([theme_icon] if theme_icon is not None else []) + [ProfileAvatar(app)],
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
        indicator_color=MINT,
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
                    skeleton_block(BODY),
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
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
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
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        navigation_bar=(
            bottom_nav(active, lambda key: page.run_task(app.open_tab, key))
            if show_nav else None
        ),
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
        ],
        # HIDDEN still enables scrolling; None keeps the outer view fixed.
        # The native navigation slot stays pinned below the scrollable body.
        scroll=None,
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


class LatestRequest:
    """Serialize identical refreshes and let only the latest filter result paint."""

    def __init__(self):
        self.revision = 0
        self.pending: dict[tuple, int] = {}
        self.key = None

    def begin(self, key: tuple) -> int | None:
        if key == self.key and key in self.pending:
            return None
        self.revision += 1
        self.key = key
        self.pending[key] = self.revision
        return self.revision

    def current(self, revision: int) -> bool:
        return revision == self.revision

    def finish(self, key: tuple, revision: int) -> None:
        if self.pending.get(key) == revision:
            self.pending.pop(key, None)


def action_row(*buttons: ft.Control) -> ft.ResponsiveRow:
    """Stack actions on small phones; share the row when there is room."""
    return ft.ResponsiveRow(
        breakpoints={"xs": 0, "sm": 380},
        spacing=SPACE_S, run_spacing=SPACE_S,
        controls=[
            ft.Column(col={"xs": 12, "sm": 12 / len(buttons)},
                      horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                      controls=[button])
            for button in buttons
        ],
    )


class FormGuard:
    """Keep edits on cancel/system back unless the user explicitly discards them."""

    def __init__(self, page, snapshot, leave, busy):
        self.page, self.snapshot, self.leave, self.busy = page, snapshot, leave, busy
        self.initial = snapshot()
        self.dialog = None

    def request_leave(self):
        if self.busy() or self.dialog is not None:
            return
        if self.snapshot() == self.initial:
            self.page.run_task(self.leave)
            return

        def close(e=None):
            self.page.pop_dialog()
            self.dialog = None

        def discard(e):
            close()
            self.page.run_task(self.leave)

        self.dialog = ft.AlertDialog(
            modal=True, title=ft.Text(t('Discard your changes?')),
            content=ft.Text(t('Your changes have not been saved.')),
            actions=[
                ft.TextButton(t("Keep editing"), on_click=close),
                ft.TextButton(t("Discard changes"), on_click=discard),
            ],
        )
        self.page.show_dialog(self.dialog)


def savings_progress(goal: dict, currency: str) -> ft.Column:
    """Truthful progress and the next milestone, shared by overview and goals."""
    from decimal import Decimal
    from theme import money

    progress = max(0.0, float(goal.get("progress_percentage") or 0))
    target = Decimal(str(goal.get("target_amount") or 0))
    saved = Decimal(str(goal.get("saved_amount") or 0))
    next_band = next((band for band in (25, 50, 75, 100) if progress < band), None)
    message = t('Goal reached · Based on your recorded savings')
    if next_band is not None:
        remaining = max(Decimal(0), target * Decimal(next_band) / 100 - saved)
        message = t('{v0} to your {v1}% milestone', v0=money(remaining, currency), v1=next_band)
    return ft.Column(spacing=SPACE_S, controls=[
        ft.Semantics(
            label=t('Savings progress: {v0} percent', v0=round(progress)),
            value=f"{round(progress)}%", exclude_semantics=True,
            content=ft.ProgressBar(value=min(progress / 100, 1), color=SUCCESS,
                                   bgcolor=BORDER, bar_height=8, border_radius=4),
        ),
        ft.Text(t('{v0} saved of {v1}', v0=money(saved, currency), v1=money(target, currency)),
                size=BODY_SM, color=MUTED),
        ft.Row(spacing=SPACE_S, controls=[
            ft.Semantics(
                expand=True,
                label=t('{v0}% milestone, ', v0=band) + (t('reached') if progress >= band else t('ahead')),
                exclude_semantics=True,
                content=ft.Container(
                    padding=ft.Padding.symmetric(vertical=SPACE_S),
                    border_radius=RADIUS_SM,
                    bgcolor=MINT if progress >= band else NOTE_BG,
                    content=ft.Column(
                        spacing=SPACE_XS,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE if progress >= band
                                    else ft.Icons.RADIO_BUTTON_UNCHECKED,
                                    size=18, color=PRIMARY if progress >= band else MUTED),
                            ft.Text(t('{v0}%', v0=band), size=CAPTION_SIZE,
                                    color=PRIMARY if progress >= band else MUTED),
                        ],
                    ),
                ),
            ) for band in (25, 50, 75, 100)
        ]),
        ft.Text(message, size=BODY_SM, color=SUCCESS),
    ])


def padded(control: ft.Control) -> ft.Container:
    """The standard body inset inside a tab screen."""

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=PAGE_PAD, vertical=SPACE_M),
        content=control,
    )


# ---------------------------------------------------------------------------
# Content pieces
# ---------------------------------------------------------------------------
def segmented(
    options: list[tuple[str, str]], value: str, on_select
) -> ft.Container:
    """Accessible single-choice control for filters and view modes."""

    segments: list[tuple[str, str]] = []
    buttons: list[ft.Button] = []
    semantics: list[ft.Semantics] = []

    def select(key: str, e) -> None:
        for (segment_key, label), button, semantic in zip(
            segments, buttons, semantics
        ):
            is_selected = segment_key == key
            button.bgcolor = PRIMARY if is_selected else SURFACE
            button.color = BG if is_selected else INK
            semantic.label = t("{v0}, selected", v0=label) if is_selected else label
            semantic.selected = is_selected

        page = e.control.page
        if page is not None:
            page.update(*buttons, *semantics)
        on_select(key)

    controls: list[ft.Control] = []
    for index, (key, label) in enumerate(options):
        button = ft.Button(
            content=label,
            color=BG if key == value else INK,
            bgcolor=PRIMARY if key == value else SURFACE,
            height=BUTTON_H,
            expand=True,
            elevation=0,
            style=ft.ButtonStyle(
                animation_duration=duration(),
                padding=ft.Padding.symmetric(horizontal=12),
                side=ft.BorderSide(0, BORDER),
                shape=ft.RoundedRectangleBorder(radius=0),
            ),
            on_click=lambda e, selected_key=key: select(selected_key, e),
        )
        semantic = ft.Semantics(
            content=button,
            expand=True,
            label=t('{v0}, selected', v0=label) if key == value else label,
            button=True,
            focusable=True,
            selected=key == value,
        )
        segments.append((key, label))
        buttons.append(button)
        semantics.append(semantic)

        if index:
            controls.append(
                ft.Container(width=1, height=BUTTON_H, bgcolor=BORDER)
            )
        controls.append(semantic)

    return ft.Container(
        width=float("inf"),
        height=BUTTON_H,
        border=ft.Border.all(1, BORDER),
        border_radius=RADIUS,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Row(spacing=0, controls=controls),
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
    *,
    featured: bool = False,
    icon=None,
) -> ft.Container:
    """A labelled money figure. `size` lets tight rows use the small scale."""

    label_control = ft.Text(label.upper(), size=CAPTION_SIZE,
                           weight=ft.FontWeight.W_600,
                           color=ON_PRIMARY if featured else MUTED)
    controls: list[ft.Control] = [
        ft.Row(controls=[
            ft.Container(
                width=36, height=36, border_radius=12,
                bgcolor=PRIMARY_DARK if featured else MINT,
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(icon, size=19, color=SURFACE if featured else PRIMARY),
            ),
            ft.Container(content=label_control, expand=True),
        ], spacing=SPACE_M) if icon is not None else label_control,
        ft.Text(value, size=size, weight=ft.FontWeight.W_700, color=INK),
    ]
    if featured:
        controls[-1].color = SURFACE
    if detail:
        controls.append(ft.Text(detail, size=BODY_SM,
                                color=ON_PRIMARY if featured else MUTED))
    result = card(
        ft.Column(
            spacing=SPACE_M,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=controls,
        ),
        padding=SPACE_XL if featured else SPACE_L,
    )
    if featured:
        result.bgcolor = PRIMARY
        result.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
            colors=[PRIMARY, PRIMARY_DARK],
        )
        result.border = None
    return result


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
        ft.Container(
            width=64, height=64, border_radius=22,
            bgcolor=MINT, alignment=ft.Alignment.CENTER,
            content=ft.Icon(icon, size=30, color=PRIMARY),
        ),
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
                content=ft.Text(t('Try again'), size=BODY_SM, color=INK),
                style=ft.ButtonStyle(
                    overlay_color={ft.ControlState.FOCUSED: BORDER,
                               ft.ControlState.PRESSED: NOTE_BG},
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
                    translated_server_text(alert.get("message")) or t('Something needs your attention.'),
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
                content=ft.Text(t('Review'), size=BODY_SM, color=INK),
                style=ft.ButtonStyle(
                    overlay_color={ft.ControlState.FOCUSED: BORDER,
                               ft.ControlState.PRESSED: NOTE_BG},
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


def nav_footer(on_back=None, on_continue=None, continue_label=t('Continue'),
               back_label=t('Back'), skip_label: str | None = None,
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
                    overlay_color={ft.ControlState.FOCUSED: BORDER,
                               ft.ControlState.PRESSED: NOTE_BG},
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
