"""Transactions list + add/edit form
(design: mobile/screens/cashflow/Screenshot *193748–193901).

The list reads GET /api/transactions for one month, passing the All / Income /
Expenses filter and the "From date (optional)" box straight through, so the
server filters and returns that month's totals.

Rows still `expected` get a "Mark received" (income) or "Mark paid" (expense)
button, which calls POST /api/transactions/{id}/confirm. Tapping a row opens
the form in edit mode.

The list response carries no currency, so it comes from the dashboard
overview, which the app already holds after login.
"""

from i18n import t

import flet as ft

from api.client import Unauthenticated, error_message
from theme import (
    BODY,
    BODY_SM,
    BORDER,
    INK,
    INPUT_SIZE,
    MUTED,
    NOTE_BG,
    SPACE_M,
    SPACE_S,
    SURFACE,
    caption,
    current_month,
    format_date,
    money,
    month_label,
    month_nav,
    primary_button,
    secondary_button,
    shown_amount,
    style_input,
    to_amount,
)
from widgets import (
    FormGuard,
    LatestRequest,
    DateField,
    card,
    empty_state,
    error_card,
    error_text,
    field_label,
    labeled,
    padded,
    page_title,
    pill,
    refresh_indicator,
    segmented,
    set_busy,
    snack,
    submit_button,
    submit_row,
    tab_view,
    tappable,
    validate_fields,
)

KINDS = [("all", t('All')), ("income", t('Income')), ("expenses", t('Expenses'))]

STATUS_OPTIONS = [
    ft.DropdownOption(key="expected", text=t('Expected')),
    ft.DropdownOption(key="received", text=t('Received / paid')),
    ft.DropdownOption(key="cancelled", text=t('Cancelled')),
]
RECURRENCE_OPTIONS = [
    ft.DropdownOption(key="none", text=t('Does not repeat')),
    ft.DropdownOption(key="daily", text=t('Daily')),
    ft.DropdownOption(key="weekly", text=t('Weekly')),
    ft.DropdownOption(key="monthly", text=t('Monthly')),
    ft.DropdownOption(key="yearly", text=t('Yearly')),
]

# Used until GET /api/transactions/options answers, and if that call fails, so
# the dropdowns are never empty.
DEFAULT_OPTIONS = {
    "income_categories": ["client_payment", "salary", "refund", "other"],
    "expense_categories": [
        "housing",
        "utilities",
        "food",
        "transport",
        "subscriptions",
        "equipment",
        "tax",
        "other",
    ],
}


def pretty(value: str | None) -> str:
    """'client_payment' -> 'Client payment'; '' for None."""

    return t((value or "").replace("_", " ").capitalize())


def status_chip(status: str) -> ft.Container:
    """Expected money is still a plan, so it gets the muted fill; a received
    or paid row sits on plain surface to read as settled."""

    label = {"expected": "Expected", "received": "Received"}.get(
        status, pretty(status)
    )
    return pill(label, bg=NOTE_BG if status == "expected" else SURFACE)


def transaction_row(item: dict, currency: str, on_confirm, on_edit) -> ft.Semantics:
    income = item.get("direction") == "income"
    amount = money(item.get("amount"), currency)
    signed = f"+{amount}" if income else f"−{amount}"

    meta = " · ".join(
        part
        for part in (
            format_date(item.get("transaction_date")),
            pretty(item.get("category")) or None,
        )
        if part
    )

    controls: list[ft.Control] = [
        ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    width=30,
                    height=30,
                    bgcolor=NOTE_BG,
                    border_radius=15,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        "+" if income else "−", size=INPUT_SIZE, color=INK
                    ),
                ),
                ft.Container(width=SPACE_M),
                ft.Column(
                    spacing=SPACE_S - 4,
                    expand=True,
                    controls=[
                        ft.Text(
                            item.get("description") or t('Transaction'),
                            size=INPUT_SIZE,
                            weight=ft.FontWeight.W_500,
                            color=INK,
                        ),
                        ft.Text(meta, size=BODY_SM - 1, color=MUTED),
                        status_chip(item.get("status") or "expected"),
                    ],
                ),
            ],
        ),
        ft.Text(signed, size=INPUT_SIZE, weight=ft.FontWeight.W_600, color=INK),
    ]

    if item.get("status") == "expected" and not item.get("is_savings_allocation"):
        controls.append(
            secondary_button(
                t('Mark received') if income else t('Mark paid'),
                lambda e, i=item: on_confirm(i),
                expand=True,
            )
        )

    row = card(ft.Column(spacing=SPACE_S + 2, controls=controls))
    return tappable(
        row,
        lambda e, i=item: on_edit(i),
        t('Edit transaction {v0}', v0=item.get('description') or 'Transaction'),
    )


class TransactionsScreen:
    def __init__(self, page: ft.Page, app):
        self.page = page
        self.app = app
        self.data: dict = {}
        self.error: str | None = None
        self.busy = False
        self.loading = False
        self.requests = LatestRequest()
        self.content = ft.Column(
            spacing=SPACE_M + 2,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[],
        )
        self.refresh_bar = refresh_indicator()
        # One view is reused so switching tabs swaps the top view instead of
        # stacking a second copy (same approach as the dashboard).
        self.view_control = tab_view(
            t('Transactions'),
            self.app,
            padded(self.content),
            active="transactions",
            route="/transactions",
            loading=self.loading,
            theme_icon=ft.IconButton(
                icon=ft.Icons.REFRESH,
                icon_size=18,
                icon_color=INK,
                tooltip=t('Refresh'),
                on_click=lambda e: self.page.run_task(self.load),
            ),
        )

    # Filters live on the app so switching tabs remembers them.
    @property
    def kind(self) -> str:
        return self.app.tx_filters.get("kind") or "all"

    @property
    def from_date(self) -> str | None:
        return self.app.tx_filters.get("from_date")

    @property
    def month(self) -> str:
        return self.app.tx_filters.get("month") or current_month()

    # ---- layout ----------------------------------------------------------
    def view(self) -> ft.View:
        return self.view_control

    def render(self):
        self.view_control.body_slot.visible = True
        self.view_control.loading_state.finish()
        controls: list[ft.Control] = [
            self.refresh_bar,
            page_title(
                t('Transactions'),
                t('Expected income stays separate until it is received.'),
            ),
            primary_button(
                t('+ Add transaction'),
                lambda e: self.page.run_task(self.app.open_transaction_form),
                expand=True,
            ),
            segmented(
                KINDS, self.kind, lambda key: self.page.run_task(self._set_kind, key)
            ),
            ft.Column(
                spacing=SPACE_S - 2,
                controls=[
                    field_label(t('From date (optional)')),
                    self._from_date_field(),
                ],
            ),
        ]

        if self.error:
            controls.append(
                error_card(
                    (t('Showing the last loaded transactions. ') if self.data else "") + self.error,
                    on_retry=lambda e: self.page.run_task(self.load),
                )
            )
            if not self.data:
                self.content.controls = controls
                self.page.update()
                return

        currency = self.data.get("currency") or "ZAR"
        items = self.data.get("items") or []
        month = self.data.get("month") or self.month

        rows: list[ft.Control] = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        month_label(month),
                        size=BODY_SM - 1,
                        weight=ft.FontWeight.W_600,
                        color=INK,
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

        if items:
            for item in items:
                rows.append(
                    transaction_row(
                        item,
                        currency,
                        on_confirm=lambda i: self.page.run_task(self._confirm, i),
                        on_edit=lambda i: self.page.run_task(
                            self.app.open_transaction_form, i
                        ),
                    )
                )
            controls.append(card(ft.Column(spacing=SPACE_M, controls=rows)))
            controls.append(
                card(
                    ft.Row(
                        controls=[
                            self._total(
                                "INCOME", self.data.get("total_income"), currency
                            ),
                            self._total(
                                "EXPENSES", self.data.get("total_expenses"), currency
                            ),
                            self._total(
                                "NET", self.data.get("net"), currency, strong=True
                            ),
                        ]
                    )
                )
            )
        else:
            controls.append(
                card(
                    ft.Column(spacing=SPACE_M, controls=rows),
                )
            )
            controls.append(
                empty_state(
                    t('No transactions in this month'),
                    t('Add one to see how it affects your balance.'),
                    icon=ft.Icons.SWAP_VERT_OUTLINED,
                    action=primary_button(
                        t('+ Add transaction'),
                        lambda e: self.page.run_task(
                            self.app.open_transaction_form
                        ),
                    ),
                )
            )

        self.content.controls = controls
        self.page.update()

    def _from_date_field(self) -> ft.Control:
        """Rebuilt on every render so it shows the date actually applied."""

        field = DateField(
            self.page,
            "",
            on_change=lambda iso: self.page.run_task(self._apply_from_date, iso),
        )
        field.field.hint_text = "dd/mm/yyyy"
        field.value = self.from_date
        return field.field

    @staticmethod
    def _total(label: str, value, currency: str, strong: bool = False) -> ft.Column:
        return ft.Column(
            expand=True,
            spacing=2,
            controls=[
                caption(label),
                ft.Text(
                    money(value, currency),
                    size=INPUT_SIZE,
                    weight=ft.FontWeight.W_700 if strong else ft.FontWeight.W_600,
                    color=INK,
                ),
            ],
        )

    # ---- data ------------------------------------------------------------
    async def load(self):
        await self._load(spinner=True)

    async def _load(self, spinner: bool):
        """`spinner` shows the skeleton on a first/open load; filter changes
        keep the list on screen and mark it busy in place."""

        key = (self.month, self.from_date, self.kind)
        revision = self.requests.begin(key)
        if revision is None:
            return
        self.loading = True
        first_open = not self.content.controls
        if first_open:
            self.view_control.loading_state.start(immediate=True)
        self.refresh_bar.visible = not first_open
        self.page.update()
        try:
            data = await self._fetch(key)
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
                self.refresh_bar.visible = False
                self.view_control.loading_state.finish()
        if self.requests.current(revision):
            self.render()

    async def _fetch(self, key):
        page = await self.app.api.transactions(
            month=key[0], from_date=key[1], kind=key[2]
        )
        if not (self.app.overview or {}).get("currency"):
            try:
                self.app.overview = await self.app.api.overview()
            except Exception:  # noqa: BLE001 - totals fall back to ZAR
                self.app.overview = dict(self.app.overview or {})
        # The list endpoint omits the currency; use the profile's.
        page["currency"] = (self.app.overview or {}).get("currency") or "ZAR"
        return page

    async def _set_kind(self, key: str):
        self.app.tx_filters["kind"] = key
        await self._load(spinner=False)

    async def _step_month(self, delta: int):
        self.app.tx_filters["month"] = month_nav(self.month, delta)
        await self._load(spinner=False)

    async def _apply_from_date(self, iso):
        self.app.tx_filters["from_date"] = iso
        await self._load(spinner=False)

    async def _confirm(self, item: dict):
        if self.busy:
            return
        self.busy = True
        self.error = None
        # Mark the whole list busy so a second row can't be confirmed while
        # the first request is still running.
        self.refresh_bar.visible = True
        self.page.update()
        try:
            await self.app.api.confirm_transaction(item["id"])
        except Unauthenticated:
            self.busy = False
            await self.app.logout()
            return
        except Exception as exc:  # noqa: BLE001 - shown above the list
            self.error = error_message(exc)
            self.busy = False
            self.refresh_bar.visible = False
            self.render()
            return
        self.busy = False
        self.refresh_bar.visible = False
        snack(
            self.page,
            t('Marked as received')
            if item.get("direction") == "income"
            else t('Marked as paid'),
        )
        await self._load(spinner=False)

    def form(self, transaction: dict | None = None) -> "TransactionForm":
        return TransactionForm(self.page, self.app, transaction)


class TransactionForm:
    """Add form (transaction=None) or edit form for an existing row."""

    def __init__(self, page: ft.Page, app, item):
        self.page = page
        self.app = app
        self.item = item or {}
        self.editing = bool(item)
        self.options: dict = dict(DEFAULT_OPTIONS)
        self.error = error_text()
        self.options_notice = ft.Text(
            t('Could not load updated categories. Standard categories are available.'),
            size=BODY_SM,
            color=MUTED,
            visible=False,
        )

        self.direction = self.item.get("direction") or "income"
        self.description = style_input(
            ft.TextField(
                label=t('e.g. Project payment'),
                value=self.item.get("description") or "",
            )
        )
        self.amount = style_input(
            ft.TextField(
                label="R 0",
                value=shown_amount(self.item.get("amount")),
                keyboard_type=ft.KeyboardType.NUMBER,
            )
        )
        self.date = DateField(page, "")
        self.date.value = self.item.get("transaction_date")

        self.status = style_input(
            ft.Dropdown(
                value=self.item.get("status") or "expected",
                options=STATUS_OPTIONS,
            )
        )
        self.category = style_input(ft.Dropdown(value=None, options=[]))
        self.recurrence = style_input(
            ft.Dropdown(
                value=self.item.get("recurrence") or "none",
                options=RECURRENCE_OPTIONS,
            )
        )
        self.notes = style_input(
            ft.TextField(
                label=t('Add context'),
                value=self.item.get("notes") or "",
                multiline=True,
                min_lines=3,
                max_lines=6,
            )
        )
        self.toggle_slot = ft.Row(controls=[])
        self.submit = submit_button(
            t('Save changes') if self.editing else t('Save transaction'),
            lambda e: self.page.run_task(self._save),
        )
        self._render()
        self._sync_categories()
        self.guard = FormGuard(page, self._snapshot, self._leave,
                               lambda: self.submit.disabled)

        self.page.run_task(self._load_options)

    # ---- options ---------------------------------------------------------
    async def _load_options(self):
        try:
            self.options = await self.app.api.transaction_options()
            untouched = self._snapshot() == self.guard.initial
            self._sync_categories()
            if untouched:
                self.guard.initial = self._snapshot()
        except Unauthenticated:
            await self.app.logout()
        except Exception:  # noqa: BLE001 - standard categories remain available
            self.options_notice.visible = True
            self._safe_update()

    def _sync_categories(self):
        keys = "income_categories" if self.direction == "income" else "expense_categories"
        allowed = self.options.get(keys) or []
        current = self.category.value or (self.item.get("category") if self.editing else None)
        self.category.options = [
            ft.DropdownOption(key=key, text=pretty(key)) for key in allowed
        ]
        self.category.value = current if current in allowed else None
        self._safe_update()

    def _safe_update(self):
        # Init runs before the form is attached to a view; updating then is
        # harmless but Flet can complain about a detached control.
        try:
            self.page.update()
        except Exception:  # noqa: BLE001 - nothing visible yet
            pass

    def _set_direction(self, direction: str):
        if direction == self.direction:
            return
        self.direction = direction
        self.toggle_slot.controls = [self._toggle()]
        self._sync_categories()

    def _toggle(self) -> ft.Control:
        return segmented(
            [("income", "Income"), ("expense", "Expense")],
            self.direction,
            self._set_direction,
        )

    # ---- layout ----------------------------------------------------------
    def view(self) -> ft.View:
        view = tab_view(
            t('Transaction form'),
            self.app,
            padded(self.body),
            active="transactions",
            route="/transactions/form",
            on_back=lambda e: self.page.run_task(self._cancel),
        )
        view.request_leave = self.guard.request_leave
        return view

    def _snapshot(self):
        return (self.direction, self.description.value, self.amount.value,
                self.date.value, self.status.value, self.category.value,
                self.recurrence.value, self.notes.value)

    def _render(self):
        self.toggle_slot.controls = [self._toggle()]
        self.body = ft.Column(
            spacing=SPACE_M + 4,
            controls=[
                page_title(
                    t('Edit transaction') if self.editing else t('Add transaction'),
                    t('Record expected and completed payments clearly.'),
                ),
                card(
                    ft.Column(
                        spacing=SPACE_M + 4,
                        controls=[
                            self.toggle_slot,
                            labeled(t('Description *'), self.description),
                            labeled(t('Amount (ZAR) *'), self.amount),
                            labeled(t('Date'), self.date.field),
                            labeled(t('Status'), self.status),
                            labeled(t('Category'), self.category),
                            self.options_notice,
                            labeled(t('Recurrence (optional)'), self.recurrence),
                            labeled(t('Notes (optional)'), self.notes),
                            self.error,
                            ft.Divider(color=BORDER),
                            submit_row(
                                lambda e: self.page.run_task(self._cancel),
                                self.submit,
                            ),
                        ],
                    )
                ),
            ],
        )

    # ---- actions ---------------------------------------------------------
    async def _cancel(self):
        self.guard.request_leave()

    async def _leave(self):
        await self.app.open_tab("transactions")

    async def _save(self):
        if self.submit.disabled:
            return
        self.error.visible = False
        from decimal import Decimal
        if not validate_fields(self.page, [
            (self.description, None if (self.description.value or "").strip()
             else t("Enter a description.")),
            (self.amount, None),
            (self.date.field, None if self.date.value else t("Choose a date.")),
        ]):
            return
        set_busy(self.submit, True)
        self.page.update()

        # Validate before the request so the spinner never hides a typo.
        try:
            description = (self.description.value or "").strip()
            amount = to_amount(self.amount.value)
            if not description:
                raise ValueError(t('Description is required.'))
            if not amount:
                self.amount.error_text = t('Enter an amount.')
                raise ValueError(t('Amount is required.'))
            if Decimal(amount) <= 0:
                self.amount.error_text = t('Amount must be greater than zero.')
                raise ValueError(self.amount.error_text)
            if not self.date.value:
                raise ValueError(t('Date is required.'))
        except ValueError as exc:
            set_busy(self.submit, False)
            self._show_error(str(exc))
            return

        # Both endpoints share these field names. `recurrence` is only sent
        # when creating: the edit schema does not accept it, and a series is
        # fixed once it exists.
        fields = {
            "direction": self.direction,
            "description": description,
            "amount": amount,
            "transaction_date": self.date.value,
            "status": self.status.value,
            "category": self.category.value,
            "notes": (self.notes.value or "").strip() or None,
        }
        try:
            if self.editing:
                # The default PATCH drops blank fields, which would keep a
                # value the user just cleared; this variant sends nulls.
                await self.app.api.clear_transaction_fields(
                    self.item["id"], **fields
                )
            else:
                fields["recurrence"] = self.recurrence.value or "none"
                await self.app.api.create_transaction(**fields)
        except Unauthenticated:
            set_busy(self.submit, False)
            await self.app.logout()
            return
        except Exception as exc:  # noqa: BLE001
            set_busy(self.submit, False)
            self._show_error(error_message(exc))
            return

        snack(
            self.page,
            t('Transaction updated') if self.editing else t('Transaction saved'),
        )
        await self.app.open_tab("transactions")

    def _show_error(self, message: str):
        self.error.value = message
        self.error.visible = True
        self.page.update()
