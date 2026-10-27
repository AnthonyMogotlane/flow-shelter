"""Cash-flow plan (design: mobile/screens/cashflow/Screenshot *192614–193209).

Built from GET /api/cashflow/timeline. The endpoint returns every row with its
running balance, the period label and the summary figures, so this screen only
decides how to draw each event:

- starting balance and confirmed events: solid ink dot, balance in ink
- pending events (expected income, unpaid commitments): hollow dot, a note
  under the label ("Upcoming", "Depends on payment arriving"), muted balance

"Until next payment" runs from today to the next expected payment; "Monthly"
covers one calendar month, stepped with the ‹ › arrows.
"""

from i18n import t
from i18n import translated_server_text

import flet as ft

from api.client import Unauthenticated, error_message
from theme import (
    BODY,
    BODY_SM,
    BORDER,
    CARD_VALUE_SM,
    INK,
    MUTED,
    SPACE_S,
    SURFACE,
    caption,
    current_month,
    format_date,
    money,
    month_label,
    month_nav,
    note,
    primary_button,
    short_date,
)
from widgets import (
    LatestRequest,
    card,
    error_card,
    padded,
    page_title,
    refresh_indicator,
    segmented,
    stat_card,
    tab_view,
)

VIEWS = [("until_next_payment", t('Until next payment')), ("monthly", t('Monthly'))]

# Default note per kind when the API does not supply one.
KIND_LABELS = {
    "income": t('Expected'),
    "expense": t('Upcoming'),
    "savings_allocation": t('Planned'),
}


def event_row(event: dict, currency: str, is_last: bool) -> ft.Row:
    """Date | rail with dot | label + note + running balance."""

    kind = event.get("kind")
    pending = bool(event.get("pending")) or (
        not event.get("confirmed") and kind != "starting_balance"
    )
    balance = money(event.get("balance"), currency)

    if kind == "starting_balance":
        detail = None
    elif pending:
        detail = translated_server_text(event.get("note")) or KIND_LABELS.get(kind, t('Expected'))
    elif kind == "savings_allocation":
        detail = t('Planned, not transferred')
    else:
        sign = "+" if kind == "income" else "−"
        moved = t('Received') if kind == "income" else t('Paid')
        detail = f"{sign}{money(event.get('amount'), currency)} · {moved}"

    dot_color = MUTED if pending else INK

    return ft.Row(
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                width=56,
                padding=ft.Padding.only(top=3),
                content=ft.Text(
                    short_date(event.get("date")), size=BODY_SM - 1, color=MUTED
                ),
            ),
            ft.Column(
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(height=4),
                    ft.Container(
                        width=9,
                        height=9,
                        shape=ft.BoxShape.CIRCLE,
                        bgcolor=SURFACE if pending else dot_color,
                        border=ft.Border.all(2, dot_color),
                    ),
                    # Connector to the next row; the last event has none.
                    ft.Container(
                        width=1,
                        bgcolor=BORDER,
                        visible=not is_last,
                        expand=True,
                        margin=ft.Margin.only(top=2),
                    ),
                ],
            ),
            ft.Container(width=12),
            ft.Container(
                expand=True,
                padding=ft.Padding.only(bottom=18 if not is_last else 4),
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            (translated_server_text(event.get("label"))
                             if kind in ("starting_balance", "savings_allocation")
                             else event.get("label")) or "",
                            size=BODY,
                            weight=ft.FontWeight.W_400
                            if pending
                            else ft.FontWeight.W_500,
                            color=INK,
                        ),
                        *(
                            [ft.Text(detail, size=BODY_SM - 1, color=MUTED)]
                            if detail
                            else []
                        ),
                        ft.Text(
                            balance,
                            size=CARD_VALUE_SM,
                            weight=ft.FontWeight.W_600,
                            color=MUTED if pending else INK,
                        ),
                    ],
                ),
            ),
        ],
    )


class CashFlowScreen:
    def __init__(self, page: ft.Page, app):
        self.page = page
        self.app = app
        self.data: dict = {}
        self.error: str | None = None
        self.loading = False
        self.requests = LatestRequest()
        self.content = ft.Column(
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[],
        )
        self.refresh_bar = refresh_indicator()
        self.view_control = tab_view(
            t('Cash flow'),
            self.app,
            padded(self.content),
            active="cashflow",
            route="/cashflow",
            loading=self.loading,
            theme_icon=ft.IconButton(
                icon=ft.Icons.REFRESH,
                icon_size=18,
                icon_color=INK,
                tooltip=t('Refresh'),
                on_click=lambda e: self.page.run_task(self.load),
            ),
        )

    # View and month live on the app so switching tabs remembers them.
    @property
    def view_name(self) -> str:
        return self.app.tab_view.get("cashflow") or "until_next_payment"

    @property
    def month(self) -> str:
        return self.app.tab_view.get("cashflow_month") or current_month()

    # ---- layout ----------------------------------------------------------
    def view(self) -> ft.View:
        return self.view_control

    def _period_header(self) -> list[ft.Control]:
        if self.view_name != "monthly":
            return [
                caption(t('SELECTED PERIOD')),
                ft.Text(
                    self._period_text(),
                    size=BODY + 3,
                    weight=ft.FontWeight.W_600,
                    color=INK,
                ),
            ]
        return [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=2,
                        expand=True,
                        controls=[
                            caption(t('SELECTED PERIOD')),
                            ft.Text(
                                self._period_text(),
                                size=BODY + 3,
                                weight=ft.FontWeight.W_600,
                                color=INK,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_size=18,
                                icon_color=INK,
                                tooltip=t('Previous month'),
                                on_click=lambda e: self.page.run_task(
                                    self._step_month, -1
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ARROW_FORWARD,
                                icon_size=18,
                                icon_color=INK,
                                tooltip=t('Next month'),
                                on_click=lambda e: self.page.run_task(
                                    self._step_month, 1
                                ),
                            ),
                        ],
                    ),
                ],
            )
        ]

    def _period_text(self):
        if self.view_name == "monthly":
            month = str(self.data.get("start_date") or self.month)[:7]
            return month_label(month).title()
        if self.data.get("start_date") and self.data.get("end_date"):
            from datetime import date
            start = str(self.data["start_date"])[:10]
            label = t("Today") if start == date.today().isoformat() else short_date(start)
            return t("{v0} – {v1}", v0=label, v1=format_date(self.data["end_date"]))
        return translated_server_text(self.data.get("period_label")) or ""

    def render(self):
        self.view_control.body_slot.visible = True
        self.view_control.loading_state.finish()
        controls: list[ft.Control] = [
            self.refresh_bar,
            page_title(
                t('Cash-flow plan'),
                t('A chronological estimate — expected money is not guaranteed.'),
            ),
            primary_button(
                t('+ Add event'),
                lambda e: self.page.run_task(self.app.open_transaction_form),
                expand=True,
            ),
            segmented(
                VIEWS,
                self.view_name,
                lambda key: self.page.run_task(self._set_view, key),
            ),
        ]

        if self.error:
            controls.append(
                error_card(
                    (t('Could not update this period. Showing the last loaded plan. ')
                     if self.data else "") + self.error,
                    on_retry=lambda e: self.page.run_task(self.load),
                )
            )
            if not self.data:
                self.content.controls = controls
                self.page.update()
                return

        currency = self.data.get("currency") or "ZAR"
        events = self.data.get("events") or []

        timeline: list[ft.Control] = []
        for index, event in enumerate(events):
            timeline.append(event_row(event, currency, index == len(events) - 1))
        if not timeline:
            # Sits inside the timeline card, so it is copy rather than a card.
            timeline.append(
                ft.Column(
                    spacing=SPACE_S,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.INSIGHTS_OUTLINED, size=24, color=MUTED),
                        ft.Text(
                            t('Nothing planned in this period yet.'),
                            size=BODY,
                            weight=ft.FontWeight.W_600,
                            color=INK,
                        ),
                        ft.Text(
                            t('Add an event to see how your balance moves.'),
                            size=BODY_SM,
                            color=MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                )
            )

        controls.append(
            card(
                ft.Column(
                    spacing=12,
                    controls=[
                        *self._period_header(),
                        ft.Divider(color=BORDER),
                        *timeline,
                    ],
                )
            )
        )
        controls.append(
            stat_card(
                t('Starting balance'),
                money(self.data.get("starting_balance"), currency),
            )
        )

        expected = float(self.data.get("expected_not_received") or 0)
        controls.append(
            stat_card(
                t('Projected end balance'),
                money(self.data.get("projected_end_balance"), currency),
                t('Includes {v0} expected, not received.', v0=money(expected, currency))
                if expected > 0
                else t('Only money already received or paid is included.'),
            )
        )

        planned = float(self.data.get("planned_savings") or 0)
        if planned > 0:
            text = (
                t('Planned savings: {v0}. This is not an automatic transfer.', v0=money(planned, currency))
            )
        else:
            text = t('Planned savings: R 0. This is not an automatic transfer.')
        controls.append(note(text))

        self.content.controls = controls
        self.page.update()

    # ---- data ------------------------------------------------------------
    async def load(self):
        await self._load(spinner=True)

    async def _load(self, spinner: bool):
        """`spinner` shows the skeleton on a first/open load; refreshes and
        filter changes keep the content and mark it busy in place."""

        key = (self.view_name, self.month if self.view_name == "monthly" else None)
        revision = self.requests.begin(key)
        if revision is None:
            return
        self.loading = True
        first_open = not self.content.controls
        self.view_control.loading_state.start(immediate=first_open)
        if not first_open:
            self.view_control.loading_state.finish()
        self._set_refreshing(not first_open)
        try:
            data = await self.app.api.timeline(view=key[0], month=key[1])
            if self.requests.current(revision):
                self.data, self.error = data, None
        except Unauthenticated:
            await self.app.logout()
            return
        except Exception as exc:  # noqa: BLE001 - shown inline
            if self.requests.current(revision):
                self.error = error_message(exc)
        finally:
            self.requests.finish(key, revision)
            if self.requests.current(revision):
                self.loading = False
                self.view_control.loading_state.finish()
                self._set_refreshing(False)
        if self.requests.current(revision):
            self.render()

    def _set_refreshing(self, busy: bool):
        """A hairline bar above the content while a filter change loads.

        It replaces nothing, so the figures stay readable and the layout does
        not jump; it only tells the user the view is catching up.
        """

        self.refresh_bar.visible = busy
        self.page.update()

    async def _set_view(self, key: str):
        self.app.tab_view["cashflow"] = key
        await self._load(spinner=False)

    async def _step_month(self, delta: int):
        self.app.tab_view["cashflow_month"] = month_nav(self.month, delta)
        await self._load(spinner=False)
