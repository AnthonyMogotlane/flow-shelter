"""Savings goals + create/edit form
(design: mobile/screens/cashflow/Screenshot *193945–194011).

Reads GET /api/goals, which marks one goal active and returns progress and a
ready-made status label. The screen shows the active goal in full (progress
bar, saved / remaining / target) with the other goals listed underneath, then
a dashed "planning another goal?" prompt.

The goal form is POST /api/goals when creating and PATCH /api/goals/{id} when
editing. FlowShelter never moves money: every figure here is what the user
recorded themselves.
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
    CAPTION_SIZE,
    HEADING,
    INK,
    INPUT_SIZE,
    MUTED,
    NOTE_BG,
    RADIUS,
    SPACE_L,
    SPACE_M,
    SPACE_S,
    SUCCESS,
    SURFACE,
    caption,
    format_date,
    money,
    primary_button,
    secondary_button,
    shown_amount,
    style_input,
    to_amount,
)
from widgets import (
    FormGuard,
    DateField,
    card,
    detail_text,
    empty_state,
    error_card,
    error_text,
    figure,
    labeled,
    page_title,
    padded,
    pill,
    refresh_indicator,
    savings_progress,
    set_busy,
    snack,
    submit_button,
    submit_row,
    tab_view,
    tappable,
    validate_fields,
)

PRIORITIES = [
    ft.DropdownOption(key="low", text=t('Low')),
    ft.DropdownOption(key="medium", text=t('Medium')),
    ft.DropdownOption(key="high", text=t('High')),
]


# Progress milestones, in order. A goal earns the highest one it has reached,
# and the badge is derived from the API's own progress figure — never stored,
# so it can't drift from the money the user actually recorded.
MILESTONES = (
    (100, t('Goal reached'), SUCCESS, SURFACE),
    (75, t('75% there'), NOTE_BG, INK),
    (50, t('Halfway there'), NOTE_BG, INK),
    (25, t('First quarter'), NOTE_BG, INK),
    (1, t('Started'), NOTE_BG, INK),
)


def milestone_badge(goal: dict) -> ft.Container | None:
    """The highest milestone a goal has reached, or None before any saving."""

    saved = float(goal.get("saved_amount") or 0)
    progress = float(goal.get("progress_percentage") or 0)
    if saved <= 0 and progress <= 0:
        return None
    for threshold, label, bg, fg in MILESTONES:
        if progress >= threshold:
            return pill(label, bg=bg, fg=fg)
    return None


def goal_card(goal: dict, currency: str, on_edit) -> ft.Semantics:
    """Active goal: status chip, progress bar and the three figures."""

    progress = float(goal.get("progress_percentage") or 0)
    badge = milestone_badge(goal)
    card_control = card(
        ft.Column(
            spacing=SPACE_M,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        caption(t('ACTIVE GOAL')),
                        *([badge] if badge is not None else []),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Text(
                            goal.get("name") or t('Goal'),
                            size=HEADING,
                            weight=ft.FontWeight.W_700,
                            color=INK,
                            expand=True,
                        ),
                        pill(translated_server_text(goal.get("status_label")) or t('No date')),
                    ],
                ),
                savings_progress(goal, currency),
                figure(t('Saved'), money(goal.get("saved_amount"), currency)),
                figure(t('Remaining'), money(goal.get("remaining"), currency)),
                figure(t('Target'), money(goal.get("target_amount"), currency)),
                detail_text(
                    t('Target date: {v0}', v0=format_date(goal.get('target_date')))
                ),
            ],
        )
    )
    return tappable(
        card_control,
        lambda e: on_edit(goal),
        t('Open savings goal {v0}', v0=goal.get('name') or 'Goal'),
    )


def goal_row(goal: dict, currency: str, on_edit) -> ft.Semantics:
    progress = float(goal.get("progress_percentage") or 0)
    row = card(
        ft.Column(
            spacing=SPACE_S,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            goal.get("name") or t('Goal'),
                            size=INPUT_SIZE,
                            weight=ft.FontWeight.W_500,
                            color=INK,
                            expand=True,
                        ),
                        ft.Text(
                            t('{v0}%', v0=round(progress)),
                            size=BODY_SM,
                            weight=ft.FontWeight.W_600,
                            color=INK,
                        ),
                    ],
                ),
                ft.ProgressBar(
                    value=min(progress / 100, 1),
                    color=INK,
                    bgcolor=BORDER,
                    bar_height=4,
                    border_radius=2,
                ),
                detail_text(
                    t('{v0} of {v1}', v0=money(goal.get('saved_amount'), currency), v1=money(goal.get('target_amount'), currency))
                ),
            ],
        )
    )
    return tappable(
        row,
        lambda e: on_edit(goal),
        t('Open savings goal {v0}', v0=goal.get('name') or 'Goal'),
    )


def new_goal_prompt(on_create) -> ft.Container:
    """Bordered box: 'Planning another goal?'"""

    return ft.Container(
        border=ft.Border.all(1, BORDER),
        border_radius=RADIUS,
        padding=SPACE_L,
        content=ft.Column(
            spacing=SPACE_S + 2,
            controls=[
                ft.Text(
                    t('Planning another goal?'),
                    size=BODY + 2,
                    weight=ft.FontWeight.W_600,
                    color=INK,
                ),
                detail_text(t('Create a goal for tax, equipment or time off.')),
                ft.Row(controls=[secondary_button(t('Create another goal'), on_create)]),
            ],
        ),
    )


class GoalsScreen:
    def __init__(self, page: ft.Page, app):
        self.page = page
        self.app = app
        self.goals: list[dict] = []
        self.error: str | None = None
        self.loading = False
        self.refresh_bar = refresh_indicator()
        self.content = ft.Column(
            spacing=SPACE_M + 2,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[],
        )
        # One view is reused so switching tabs swaps the top view instead of
        # stacking a second copy (same approach as the dashboard).
        self.view_control = tab_view(
            t('Goals'),
            self.app,
            padded(self.content),
            active="goals",
            route="/goals",
            loading=self.loading,
            theme_icon=ft.IconButton(
                icon=ft.Icons.REFRESH,
                icon_size=18,
                icon_color=INK,
                tooltip=t('Refresh'),
                on_click=lambda e: self.page.run_task(self.load),
            ),
        )

    def view(self) -> ft.View:
        return self.view_control

    def render(self):
        self.view_control.body_slot.visible = True
        self.view_control.loading_state.finish()
        currency = (self.app.overview or {}).get("currency") or "ZAR"
        controls: list[ft.Control] = [
            self.refresh_bar,
            page_title(
                t('Savings goals'),
                t('Track contributions manually. FlowShelter does not move money.'),
            ),
            primary_button(
                t('+ Add goal'),
                lambda e: self.page.run_task(self.app.open_goal_form),
                expand=True,
            ),
        ]

        if self.error:
            controls.append(
                error_card(
                    self.error,
                    on_retry=lambda e: self.page.run_task(self.load),
                )
            )

        active = next((g for g in self.goals if g.get("is_active")), None)
        active_id = (active or {}).get("id")
        others = [g for g in self.goals if g.get("id") != active_id]

        on_edit = lambda g: self.page.run_task(self.app.open_goal_form, g)

        if active:
            controls.append(goal_card(active, currency, on_edit))
        elif not self.error:
            controls.append(
                empty_state(
                    t('No savings goal yet'),
                    t('Create one to start tracking progress. You record every contribution yourself.'),
                    icon=ft.Icons.FLAG_OUTLINED,
                )
            )

        for goal in others:
            controls.append(goal_row(goal, currency, on_edit))

        controls.append(
            new_goal_prompt(
                lambda e: self.page.run_task(self.app.open_goal_form)
            )
        )

        self.content.controls = controls
        self.page.update()

    async def load(self):
        if self.loading:
            return
        self.loading = True
        session_revision = getattr(self.app, "session_revision", 0)
        first_open = not self.content.controls
        if first_open:
            self.view_control.loading_state.start(immediate=True)
        if not first_open:
            # Content is already on screen: mark it busy rather than blank it.
            self.refresh_bar.visible = True
        self.page.update()
        try:
            goals = await self.app.api.goals() or []
            if session_revision != getattr(self.app, "session_revision", 0):
                return
            self.goals = goals
            self.error = None
            if not (self.app.overview or {}).get("currency"):
                try:
                    self.app.overview = await self.app.api.overview()
                except Exception:  # noqa: BLE001 - ZAR fallback
                    self.app.overview = dict(self.app.overview or {})
        except Unauthenticated:
            await self.app.logout()
            return
        except Exception as exc:  # noqa: BLE001 - shown inline
            self.error = error_message(exc)
        finally:
            self.loading = False
            self.refresh_bar.visible = False
            self.view_control.loading_state.finish()
        self.render()
        self.app.note_goal_progress(self.goals)

    def form(self, goal: dict | None = None) -> "GoalForm":
        return GoalForm(self.page, self.app, goal)


class GoalForm:
    """'Create or edit goal' — name, target, saved so far, date."""

    def __init__(self, page: ft.Page, app, goal):
        self.page = page
        self.app = app
        self.goal = goal or {}
        self.editing = bool(goal)
        self.error = error_text()

        self.name = style_input(
            ft.TextField(
                label=t('e.g. Tax reserve'),
                value=self.goal.get("name") or "",
            )
        )
        self.target = style_input(
            ft.TextField(
                label="R 0",
                value=shown_amount(self.goal.get("target_amount")),
                keyboard_type=ft.KeyboardType.NUMBER,
            )
        )
        self.saved = style_input(
            ft.TextField(
                label="R 0",
                value=shown_amount(self.goal.get("saved_amount")),
                keyboard_type=ft.KeyboardType.NUMBER,
            )
        )
        self.target_date = DateField(page, "")
        self.target_date.value = self.goal.get("target_date")
        self.priority = style_input(
            ft.Dropdown(
                value=self.goal.get("priority") or "medium", options=PRIORITIES
            )
        )
        self.submit = submit_button(
            t('Save changes') if self.editing else t('Create goal'),
            lambda e: self.page.run_task(self._save),
        )
        self.guard = FormGuard(page, self._snapshot, self._leave,
                               lambda: self.submit.disabled)

        self.body = ft.Column(
            spacing=SPACE_M + 4,
            controls=[
                page_title(
                    t('Edit goal') if self.editing else t('Create a goal'),
                    t('A goal is a target you track yourself. Nothing is transferred automatically.'),
                ),
                card(
                    ft.Column(
                        spacing=SPACE_M + 4,
                        controls=[
                            labeled(t('Goal name *'), self.name),
                            labeled(t('Target amount (ZAR) *'), self.target),
                            labeled(t('Current saved amount'), self.saved),
                            labeled(t('Target date (optional)'), self.target_date.field),
                            labeled(t('Priority'), self.priority),
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

    def view(self) -> ft.View:
        view = tab_view(
            t('Goal form'),
            self.app,
            padded(self.body),
            active="goals",
            route="/goals/form",
            on_back=lambda e: self.page.run_task(self._cancel),
        )
        view.request_leave = self.guard.request_leave
        return view

    def _snapshot(self):
        return (self.name.value, self.target.value, self.saved.value,
                self.target_date.value, self.priority.value)

    async def _cancel(self):
        self.guard.request_leave()

    async def _leave(self):
        await self.app.open_tab("goals")

    async def _save(self):
        if self.submit.disabled:
            return
        self.error.visible = False
        from decimal import Decimal
        if not validate_fields(self.page, [
            (self.name, None if (self.name.value or "").strip() else t("Enter a goal name.")),
            (self.target, None), (self.saved, None),
        ]):
            return
        try:
            name = (self.name.value or "").strip()
            target = to_amount(self.target.value)
            saved = to_amount(self.saved.value) or "0.00"
            if not name:
                raise ValueError(t('Goal name is required.'))
            if not target:
                self.target.error_text = t('Enter a target amount.')
                raise ValueError(t('Target amount is required.'))
            if Decimal(target) <= 0:
                self.target.error_text = t('Target must be greater than zero.')
                raise ValueError(self.target.error_text)
            if Decimal(saved) < 0:
                self.saved.error_text = t('Saved amount cannot be negative.')
                raise ValueError(self.saved.error_text)
        except ValueError as exc:
            self._show_error(str(exc))
            return

        set_busy(self.submit, True)
        self.page.update()

        fields = {
            "name": name,
            "target_amount": target,
            "saved_amount": saved,
            "priority": self.priority.value,
        }
        try:
            if self.editing:
                # The goal-update schema reads null as "clear the date", so
                # send it even when the user emptied the field.
                await self.app.api.clear_goal_fields(
                    self.goal["id"],
                    **fields,
                    target_date=self.target_date.value,
                )
            else:
                if self.target_date.value:
                    fields["target_date"] = self.target_date.value
                await self.app.api.create_goal(**fields)
        except Unauthenticated:
            set_busy(self.submit, False)
            await self.app.logout()
            return
        except Exception as exc:  # noqa: BLE001
            set_busy(self.submit, False)
            self._show_error(error_message(exc))
            return

        snack(self.page, t('Goal updated') if self.editing else t('Goal saved'))
        await self.app.open_tab("goals")

    def _show_error(self, message: str):
        self.error.value = message
        self.error.visible = True
        self.page.update()
