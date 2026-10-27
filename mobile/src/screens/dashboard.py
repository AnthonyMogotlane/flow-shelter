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

from i18n import t

from datetime import datetime

import flet as ft

from api.client import Unauthenticated, error_message
from theme import (
    BORDER,
    BODY,
    BODY_SM,
    CAPTION_SIZE,
    CARD_VALUE,
    HEADING,
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
    secondary_button,
    short_date,
    text_button,
)
from widgets import (
    action_row,
    alert_banner,
    card,
    detail_text,
    empty_state,
    error_card,
    heading,
    page_title,
    refresh_indicator,
    savings_progress,
    stat_card,
    tab_view,
)


def greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return t('Good morning')
    if hour < 18:
        return t('Good afternoon')
    return t('Good evening')


def balance_bars(series: list[tuple[str, float]], currency: str) -> ft.Control:
    """A small bar sketch of the running balance from the cash-flow plan.

    Flet 1.0.5 ships no chart control, so this draws the timeline's own
    balances as thin bars with the end value labelled. It reads recorded
    events; it is not a forecast, and it draws nothing when there is
    nothing to draw.
    """

    if not series:
        return detail_text(t('No planned events yet.'))

    visible_series = series[-5:]
    values = [value for _, value in visible_series]
    low = min(values + [0.0])
    high = max(values + [1.0])
    span = high - low or 1.0
    bars: list[ft.Control] = []
    for date_text, value in visible_series:
        height = 6 + 46 * (value - low) / span
        bars.append(
            ft.Semantics(
                expand=True,
                label=f"{short_date(date_text)}: {money(value, currency)}",
                exclude_semantics=True,
                content=ft.Column(
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        height=height,
                        width=6,
                        border_radius=3,
                        bgcolor=INK if value >= 0 else MUTED,
                        tooltip=f"{short_date(date_text)}: {money(value, currency)}",
                    ),
                    ft.Text(
                        short_date(date_text),
                        size=CAPTION_SIZE - 1,
                        color=MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                ),
            )
        )
    return ft.Column(
        spacing=SPACE_S,
        controls=[
            ft.Container(
                content=ft.Row(
                    spacing=SPACE_XS,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=bars,
                ),
            ),
            detail_text(
                t('Latest planned balances from {v0} to {v1}, ending at {v2}.', v0=short_date(visible_series[0][0]), v1=short_date(visible_series[-1][0]), v2=money(visible_series[-1][1], currency))
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
        self.loading = False
        self.refresh_bar = refresh_indicator()
        self.content = ft.Column(
            spacing=SPACE_M,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[],
        )

        # Flet 1.x has no pull-to-refresh control; the dashboard re-fetches
        # every time it is opened through app.open_dashboard(). One view
        # object is reused, so switching tabs swaps the top view instead of
        # stacking a second dashboard.

        self.view_control = tab_view(
            t('Overview'),
            app,
            self._padded(),
            active="overview",
            loading=True,
            theme_icon=ft.IconButton(
                icon=ft.Icons.REFRESH,
                icon_size=18,
                icon_color=INK,
                tooltip=t('Refresh'),
                on_click=lambda e: self.page.run_task(self.load),
            ),
        )

    def _padded(self) -> ft.Container:
        return ft.Container(
            width=float("inf"),
            padding=ft.Padding.symmetric(
                horizontal=SPACE_M + SPACE_XS, vertical=SPACE_M
            ),
            content=self.content,
        )

    # ---- data ------------------------------------------------------------
    def view(self) -> ft.View:
        return self.view_control

    async def load(self):
        if self.loading:
            return
        self.loading = True
        try:
            await self._load()
        finally:
            self.loading = False
            self.refresh_bar.visible = False
            self.view_control.loading_state.finish()
            self.page.update()

    async def _load(self):
        session_revision = getattr(self.app, "session_revision", 0)
        self.error = None
        # First open has nothing to keep on screen, so its skeleton shows at
        # once; a refresh keeps the old figures visible behind a thin bar.
        first_open = not self.content.controls
        if first_open:
            self.view_control.loading_state.start(immediate=True)
        if not first_open:
            self.refresh_bar.visible = True
        self.page.update()
        try:
            overview = await self.app.api.overview()
            if session_revision != getattr(self.app, "session_revision", 0):
                return
            self.app.overview = overview
        except Unauthenticated:
            self.loading = False
            self.view_control.loading_state.finish()
            self.refresh_bar.visible = False
            await self.app.logout()
            return
        except Exception as exc:  # noqa: BLE001 - shown with a retry
            self.error = error_message(exc)
            self.loading = False
            self.render()
            return

        # Paint the core figures before fetching the optional balance sketch.
        self.render()
        self.refresh_bar.visible = True
        self.page.update()

        # The balance sketch is optional: if the timeline can't be fetched
        # the dashboard still works, just without the card.
        try:
            timeline = await self.app.api.timeline(view="until_next_payment")
            if session_revision != getattr(self.app, "session_revision", 0):
                return
            self.series = balance_series(timeline.get("events"))
        except Unauthenticated:
            self.loading = False
            self.refresh_bar.visible = False
            await self.app.logout()
            return
        except Exception:  # noqa: BLE001 - keep a prior chart on refresh
            self.chart_error = True
        else:
            self.chart_error = False

        self.loading = False
        self.render()
        self.app.note_goal_progress(self.app.overview.get("savings_goals"))

    def render(self):
        self.view_control.body_slot.visible = True
        self.view_control.loading_state.finish()
        self.refresh_bar.visible = False

        if self.error is not None and not self.app.overview:
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
                t('A clear view of your plan before {v0}.', v0=format_date(next_payment['expected_date']))
            )
        else:
            lead = t('A clearer picture starts with your next expected payment.')

        controls: list[ft.Control] = [
            self.refresh_bar,
            page_title(t("{v0}, {v1}", v0=greeting(), v1=name), lead),
        ]
        if self.error:
            controls.insert(2, error_card(
                t('Could not refresh. Showing the last loaded figures. {v0}', v0=self.error),
                on_retry=lambda e: self.page.run_task(self.load)))
        if getattr(self, "chart_error", False):
            controls.append(error_card(
                t('The planned balance chart could not be refreshed.'),
                on_retry=lambda e: self.page.run_task(self.load)))

        for alert in alerts[:2]:
            controls.append(
                alert_banner(
                    alert,
                    lambda e: self.page.run_task(self.app.open_tab, "cashflow"),
                )
            )

        controls.append(
            stat_card(
                t('Available now'),
                money(overview.get("available_now"), currency),
                t('Confirmed money you can use today'),
                featured=True,
                icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
            )
        )
        controls.append(action_row(
            primary_button(t('+ Add transaction'), lambda e: self.page.run_task(
                self.app.open_transaction_form), expand=True),
            secondary_button(t('+ Add goal'), lambda e: self.page.run_task(
                self.app.open_goal_form), expand=True),
        ))
        controls.append(
            stat_card(
                t('Projected after planned events'),
                money(overview.get("projected_balance"), currency),
                t('Estimate if expected income arrives')
                if overview.get("forecast_is_estimate", True)
                else t('Projected from your latest update'),
                icon=ft.Icons.INSIGHTS_OUTLINED,
            )
        )

        if self.series:
            controls.append(
                card(
                    ft.Column(
                        spacing=SPACE_M,
                        controls=[
                            caption(t('PLANNED BALANCE')),
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
                                t('NEXT EXPECTED PAYMENT'),
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
                                t('{v0} · {v1}', v0=next_payment.get('source') or 'Expected', v1=format_date(next_payment.get('expected_date'))),
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
                            caption(t('SAVINGS GOAL')),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(goal.get("name") or t('Goal'), size=HEADING,
                                            color=INK, expand=True),
                                    ft.Text(
                                        t('{v0}%', v0=round(goal.get('progress_percentage') or 0)),
                                        size=BODY,
                                        weight=ft.FontWeight.W_600,
                                        color=INK,
                                    ),
                                ],
                            ),
                            savings_progress(goal, currency),
                            text_button(t('View savings goals'), lambda e:
                                self.page.run_task(self.app.open_tab, "goals")),
                        ],
                    )
                )
            )

        if not goals and (alerts or next_payment):
            controls.append(card(ft.Column(spacing=SPACE_S, controls=[
                caption(t('YOUR NEXT STEP')),
                heading(t('Choose a savings goal')),
                detail_text(t('Pick a target that matters to you. There is no required amount or schedule; progress follows what you record.')),
                text_button(t('Create a goal'), lambda e: self.page.run_task(
                    self.app.open_goal_form)),
            ])))

        if not goals and not alerts and not next_payment:
            # A brand-new plan: everything below is built from what the user
            # enters, so point at the two things that make it useful.
            controls.append(
                empty_state(
                    t('Nothing to show yet'),
                    t('Add an expected payment and a savings goal. Your forecast and progress build from what you enter.'),
                    icon=ft.Icons.START_OUTLINED,
                    action=ft.Row(
                        spacing=SPACE_S,
                        controls=[
                            ft.Column(
                                expand=True,
                                controls=[
                                    primary_button(
                                        t('+ Add transaction'),
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
                                        t('+ Add goal'),
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
                        t('Edit my plan'),
                        lambda e: self.page.run_task(self.app.start_onboarding),
                    )
                ],
            )
        )

        self.content.controls = controls
        self.page.update()
