"""Home dashboard (design: Screenshot 2026-10-25 080930.png).

Built from GET /api/dashboard/overview, which already includes the alerts,
so the alert banner, the money cards and the greeting all come from one
response, re-fetched every time the screen opens.

The balance card also plots the real running balances from
GET /api/cashflow/timeline. If that call fails the chart is simply left out
— the money figures above it never change.

The bottom bar is shared with the Cash flow, Transactions and Goals screens.
Every figure here comes from the API; nothing is estimated in the UI.
"""

from datetime import datetime

import flet as ft

from api.client import Unauthenticated, error_message
from theme import (
    BORDER,
    BODY,
    BODY_SM,
    CAPTION_SIZE,
    CARD_VALUE,
    INK,
    MUTED,
    ON_INK,
    ON_INK_MUTED,
    RADIUS,
    SPACE_L,
    SPACE_M,
    SPACE_S,
    SURFACE,
    SPACE_XS,
    balance_series,
    caption,
    format_date,
    money,
    primary_button,
    reduce_motion,
    secondary_button,
    short_date,
    text_button,
)
from widgets import (
    alert_banner,
    card,
    detail_text,
    empty_state,
    error_card,
    heading,
    page_title,
    refresh_indicator,
    stat_card,
    tab_view,
)


def greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def balance_bars(series: list[tuple[str, float]], currency: str) -> ft.Control:
    """A small bar sketch of the running balance from the cash-flow plan.

    Flet 1.0.5 ships no chart control, so this draws the timeline's own
    balances as thin bars with the end value labelled. It reads recorded
    events; it is not a forecast, and it draws nothing when there is
    nothing to draw.
    """

    if not series:
        return detail_text("No planned events yet.")

    values = [value for _, value in series]
    low = min(values + [0.0])
    high = max(values + [1.0])
    span = high - low or 1.0
    bars: list[ft.Control] = []
    for date_text, value in series[-14:]:
        height = 6 + 46 * (value - low) / span
        bars.append(
            ft.Column(
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=[
                    ft.Container(
                        height=height,
                        width=6,
                        border_radius=3,
                        bgcolor=INK if value >= 0 else MUTED,
                    ),
                    ft.Text(
                        short_date(date_text),
                        size=CAPTION_SIZE - 2,
                        color=MUTED,
                        no_wrap=True,
                    ),
                ],
            )
        )
    return ft.Column(
        spacing=SPACE_S,
        controls=[
            ft.Container(
                height=62,
                content=ft.Row(
                    spacing=SPACE_XS,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=bars,
                ),
            ),
            detail_text(
                f"Planned balances from {short_date(series[0][0])} to "
                f"{short_date(series[-1][0])}, ending at "
                f"{money(series[-1][1], currency)}."
            ),
        ],
    )


class DashboardScreen:
    def __init__(self, page: ft.Page, app):
        self.page = page
        self.app = app
        self.default_currency = "ZAR"

        self.series: list[tuple[str, float]] = []
        self.error: str | None = None
        self.loading = True
        self.refresh_bar = refresh_indicator()
        self.content = ft.Column(spacing=SPACE_M, controls=[])

        # Flet 1.x has no pull-to-refresh control; the dashboard re-fetches
        # every time it is opened through app.open_dashboard(). One view
        # object is reused, so switching tabs swaps the top view instead of
        # stacking a second dashboard.
        #
        # Motion is a per-device display choice, so its switch lives in the
        # dashboard header rather than in the plan data.
        self.motion_button = ft.IconButton(
            icon_size=18,
            icon_color=INK,
            on_click=lambda e: self.page.run_task(self._toggle_motion),
        )
        self._paint_motion_button()

        self.view_control = tab_view(
            "Overview",
            app,
            self._padded(),
            active="overview",
            loading=True,
            theme_icon=ft.Row(
                spacing=0,
                controls=[
                    self.motion_button,
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        icon_size=18,
                        icon_color=INK,
                        tooltip="Refresh",
                        on_click=lambda e: self.page.run_task(self.load),
                    ),
                ],
            ),
        )

    def _paint_motion_button(self):
        """Match the icon and tooltip to the current setting."""

        reduced = reduce_motion()
        self.motion_button.icon = (
            ft.Icons.SETTINGS_OUTLINED if reduced else ft.Icons.SETTINGS
        )
        self.motion_button.tooltip = "Turn on motion" if reduced else "Reduce motion"

    async def _toggle_motion(self):
        await self.app.save_reduce_motion(not reduce_motion())
        self._paint_motion_button()
        self.page.update()

    def _padded(self) -> ft.Container:
        return ft.Container(
            padding=ft.Padding.symmetric(
                horizontal=SPACE_M + SPACE_XS, vertical=SPACE_M
            ),
            content=self.content,
        )

    # ---- data ------------------------------------------------------------
    def view(self) -> ft.View:
        return self.view_control

    async def load(self):
        self.loading = True
        self.error = None
        # First open has nothing to keep on screen, so its skeleton shows at
        # once; a refresh keeps the old figures visible behind a thin bar.
        first_open = not self.content.controls
        self.view_control.loading_state.start(immediate=first_open)
        if not first_open:
            self.refresh_bar.visible = True
        self.page.update()
        try:
            self.app.overview = await self.app.api.overview()
        except Unauthenticated:
            await self.app.logout()
            return
        except Exception as exc:  # noqa: BLE001 - shown with a retry
            self.error = error_message(exc)
            self.loading = False
            self.render()
            return

        # The balance sketch is optional: if the timeline can't be fetched
        # the dashboard still works, just without the card.
        try:
            timeline = await self.app.api.timeline(view="until_next_payment")
            self.series = balance_series(timeline.get("events"))
        except Exception:  # noqa: BLE001 - optional card
            self.series = []

        self.loading = False
        self.render()
        self.app.note_goal_progress(self.app.overview.get("savings_goals"))

    def render(self):
        self.view_control.body_slot.visible = True
        self.view_control.loading_state.finish()
        self.refresh_bar.visible = False

        if self.error is not None:
            self.content.controls = [
                error_card(
                    self.error,
                    on_retry=lambda e: self.page.run_task(self.load),
                )
            ]
            self.page.update()
            return

        overview = self.app.overview or {}
        currency = overview.get("currency") or self.default_currency
        user = overview.get("user") or {}
        name = (user.get("name") or "").split(" ")[0] or "there"
        next_payment = overview.get("next_expected_payment") or {}
        alerts = overview.get("alerts") or []

        if next_payment.get("expected_date"):
            lead = (
                "Here is what needs your attention before "
                f"{format_date(next_payment['expected_date'])}."
            )
        else:
            lead = "Add an expected payment to see what is coming up."

        controls: list[ft.Control] = [
            self.refresh_bar,
            page_title(f"{greeting()}, {name}", lead),
            ft.Row(
                spacing=SPACE_S,
                controls=[
                    ft.Column(
                        expand=True,
                        controls=[
                            primary_button(
                                "+ Add transaction",
                                lambda e: self.page.run_task(
                                    self.app.open_transaction_form
                                ),
                                expand=True,
                            )
                        ],
                    ),
                    ft.Column(
                        expand=True,
                        controls=[
                            secondary_button(
                                "+ Add goal",
                                lambda e: self.page.run_task(
                                    self.app.open_goal_form
                                ),
                                expand=True,
                            )
                        ],
                    ),
                ],
            ),
        ]

        for alert in alerts[:2]:
            controls.append(
                alert_banner(
                    alert,
                    lambda e: self.page.run_task(self.app.open_tab, "cashflow"),
                )
            )

        controls.append(
            stat_card(
                "Available now",
                money(overview.get("available_now"), currency),
                "Confirmed money you can use today",
            )
        )
        controls.append(
            stat_card(
                "Projected after planned events",
                money(overview.get("projected_balance"), currency),
                "Estimate if expected income arrives"
                if overview.get("forecast_is_estimate", True)
                else "Projected from your latest update",
            )
        )

        if self.series:
            controls.append(
                card(
                    ft.Column(
                        spacing=SPACE_M,
                        controls=[
                            caption("PLANNED BALANCE"),
                            balance_bars(self.series, currency),
                        ],
                    )
                )
            )

        if next_payment:
            controls.append(
                ft.Container(
                    bgcolor=INK,
                    border_radius=RADIUS,
                    padding=SPACE_L,
                    content=ft.Column(
                        spacing=SPACE_S - 2,
                        controls=[
                            ft.Text(
                                "NEXT EXPECTED PAYMENT",
                                size=CAPTION_SIZE,
                                weight=ft.FontWeight.W_600,
                                color=ON_INK_MUTED,
                            ),
                            ft.Text(
                                money(next_payment.get("amount"), currency),
                                size=CARD_VALUE,
                                weight=ft.FontWeight.W_700,
                                color=SURFACE,
                            ),
                            ft.Text(
                                f"{next_payment.get('source') or 'Expected'} · "
                                f"{format_date(next_payment.get('expected_date'))}",
                                size=BODY_SM,
                                color=ON_INK,
                            ),
                        ],
                    ),
                )
            )

        goals = overview.get("savings_goals") or []
        if goals:
            goal = goals[0]
            controls.append(
                card(
                    ft.Column(
                        spacing=SPACE_S,
                        controls=[
                            caption("SAVINGS GOAL"),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    heading(goal.get("name") or "Goal"),
                                    ft.Text(
                                        f"{round(goal.get('progress_percentage') or 0)}%",
                                        size=BODY,
                                        weight=ft.FontWeight.W_600,
                                        color=INK,
                                    ),
                                ],
                            ),
                            ft.ProgressBar(
                                value=min(
                                    float(goal.get("progress_percentage") or 0) / 100,
                                    1,
                                ),
                                color=INK,
                                bgcolor=BORDER,
                                bar_height=6,
                                border_radius=3,
                            ),
                            ft.Text(
                                f"{money(goal.get('saved_amount'), currency)} saved of "
                                f"{money(goal.get('target_amount'), currency)}",
                                size=BODY_SM,
                                color=MUTED,
                            ),
                        ],
                    )
                )
            )

        if not goals and not alerts and not next_payment:
            # A brand-new plan: everything below is built from what the user
            # enters, so point at the two things that make it useful.
            controls.append(
                empty_state(
                    "Nothing to show yet",
                    "Add an expected payment and a savings goal. Your "
                    "forecast and progress build from what you enter.",
                    icon=ft.Icons.START_OUTLINED,
                    action=ft.Row(
                        spacing=SPACE_S,
                        controls=[
                            ft.Column(
                                expand=True,
                                controls=[
                                    primary_button(
                                        "+ Add transaction",
                                        lambda e: self.page.run_task(
                                            self.app.open_transaction_form
                                        ),
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                expand=True,
                                controls=[
                                    secondary_button(
                                        "+ Add goal",
                                        lambda e: self.page.run_task(
                                            self.app.open_goal_form
                                        ),
                                        expand=True,
                                    )
                                ],
                            ),
                        ],
                    ),
                )
            )

        controls.append(
            ft.Row(
                controls=[
                    text_button(
                        "Edit my plan",
                        lambda e: self.page.run_task(self.app.start_onboarding),
                    )
                ],
            )
        )

        self.content.controls = controls
        self.page.update()
