"""Regression coverage for slow networks, mobile forms and truthful progress."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import flet as ft
import pytest

from api.client import Api
from app import FlowShelterApp
from screens.cashflow import CashFlowScreen
from screens.dashboard import DashboardScreen
from screens.goals import GoalForm, GoalsScreen
from screens.onboarding import CommitmentsStep
from screens.profile import ProfileScreen
from screens.transactions import TransactionForm, TransactionsScreen
from theme import to_amount
from widgets import FormGuard, LatestRequest, ProfileAvatar, initials, savings_progress, tab_view


def test_navigation_is_pinned_outside_the_scrollable_body():
    page = Page()
    app = make_app(page)
    view = tab_view("Transactions", app, ft.Column(), active="transactions")
    assert isinstance(view.navigation_bar, ft.NavigationBar)
    assert view.navigation_bar.selected_index == 2
    assert view.scroll is None
    assert view.spacing == 0
    assert view.body_slot.expand is True
    assert view.body_slot.scroll == ft.ScrollMode.AUTO
    form = tab_view("Edit", app, ft.Column(), active="transactions",
                    on_back=lambda e: None)
    assert form.navigation_bar is None
    assert form.body_slot.scroll == ft.ScrollMode.AUTO


class Page:
    def __init__(self):
        self.views = []
        self.tasks = []
        self.dialogs = []

    def update(self, *args):
        pass

    def run_task(self, handler, *args):
        self.tasks.append((handler, args))

    def show_dialog(self, dialog):
        self.dialogs.append(dialog)

    def pop_dialog(self):
        self.dialogs.pop()


def make_app(page):
    return SimpleNamespace(
        page=page, overview={"currency": "ZAR"}, api=SimpleNamespace(),
        open_tab=AsyncMock(), logout=AsyncMock(),
        open_transaction_form=AsyncMock(), open_goal_form=AsyncMock(),
        save_reduce_motion=AsyncMock(), note_goal_progress=lambda goals: None,
        tx_filters={"kind": "all", "month": "2026-10"},
        tab_view={"cashflow": "monthly", "cashflow_month": "2026-10"},
    )


def test_latest_request_handles_returning_to_an_inflight_filter():
    requests = LatestRequest()
    first = requests.begin(("all",))
    assert requests.begin(("all",)) is None
    second = requests.begin(("income",))
    third = requests.begin(("all",))
    requests.finish(("all",), first)
    assert not requests.current(first)
    assert not requests.current(second)
    assert requests.current(third)
    assert requests.begin(("all",)) is None


@pytest.mark.parametrize("screen_type", [TransactionsScreen, CashFlowScreen])
def test_latest_filter_response_wins_and_cleans_up_loading(screen_type):
    async def scenario():
        page = Page()
        app = make_app(page)
        old, new = asyncio.Future(), asyncio.Future()
        fetch = AsyncMock(side_effect=lambda **kwargs: None)

        async def response(**kwargs):
            current = kwargs.get("kind", kwargs.get("month"))
            return await (old if current in ("all", "2026-10") else new)

        fetch.side_effect = response
        app.api.transactions = fetch
        app.api.timeline = fetch
        screen = screen_type(page, app)
        first = asyncio.create_task(screen.load())
        await asyncio.sleep(0)
        if screen_type is TransactionsScreen:
            app.tx_filters["kind"] = "income"
        else:
            app.tab_view["cashflow_month"] = "2026-11"
        second = asyncio.create_task(screen.load())
        await asyncio.sleep(0)
        new.set_result({"marker": "new", "events": [], "items": []})
        await second
        old.set_result({"marker": "old", "events": [], "items": []})
        await first
        assert screen.data["marker"] == "new"
        assert screen.loading is False
        assert screen.refresh_bar.visible is False
        assert screen.view_control.loading_state.skeleton.visible is False

    asyncio.run(scenario())


def test_confirmation_failure_stays_visible_without_refetching():
    async def scenario():
        page = Page()
        app = make_app(page)
        app.api.confirm_transaction = AsyncMock(side_effect=RuntimeError("Offline"))
        app.api.transactions = AsyncMock()
        screen = TransactionsScreen(page, app)
        screen.data = {"items": [], "month": "2026-10"}
        await screen._confirm({"id": 1, "direction": "income"})
        assert screen.error
        assert screen.busy is False
        assert screen.refresh_bar.visible is False
        app.api.transactions.assert_not_called()

    asyncio.run(scenario())


def test_dashboard_renders_core_figures_before_chart_finishes():
    async def scenario():
        page = Page()
        app = make_app(page)
        chart = asyncio.Future()
        app.api.overview = AsyncMock(return_value={"available_now": "120"})

        async def timeline(**kwargs):
            return await chart

        app.api.timeline = timeline
        screen = DashboardScreen(page, app)
        task = asyncio.create_task(screen.load())
        await asyncio.sleep(0)
        assert screen.content.controls
        assert screen.view_control.body_slot.visible
        assert screen.refresh_bar.visible
        await screen.load()  # duplicate refresh is ignored
        app.api.overview.assert_awaited_once()
        chart.set_result({"events": []})
        await task
        assert not screen.loading
        assert not screen.refresh_bar.visible

    asyncio.run(scenario())


def test_tab_destination_is_visible_before_network_returns():
    async def scenario():
        app = FlowShelterApp.__new__(FlowShelterApp)
        app.page = Page()
        app.page.views = [SimpleNamespace(route="/overview")]
        app.busy = False
        app.cashflow = app.transactions = None
        pending = asyncio.Future()
        view = SimpleNamespace(route="/goals")

        async def load():
            assert app.page.views[-1] is view
            await pending

        app.goals = SimpleNamespace(view=lambda: view, load=load)
        task = asyncio.create_task(app.open_tab("goals"))
        await asyncio.sleep(0)
        await app.open_tab("goals")
        assert len(app.page.views) == 1
        pending.set_result(None)
        await task
        assert not app.busy

    asyncio.run(scenario())


def test_form_guard_keeps_changes_until_explicit_discard():
    page = Page()
    values = ["original"]
    leave = AsyncMock()
    guard = FormGuard(page, lambda: tuple(values), leave, lambda: False)
    values[0] = "edited"
    guard.request_leave()
    guard.request_leave()
    assert len(page.dialogs) == 1
    page.dialogs[0].actions[0].on_click(None)
    assert not page.tasks
    assert values == ["edited"]
    guard.request_leave()
    page.dialogs[0].actions[1].on_click(None)
    assert page.tasks == [(leave, ())]


@pytest.mark.parametrize("form_type", [GoalForm, TransactionForm])
def test_invalid_forms_show_field_errors_without_sending_requests(form_type):
    async def scenario():
        page = Page()
        app = make_app(page)
        form = form_type(page, app, None)
        await form._save()
        control = form.name if form_type is GoalForm else form.description
        assert control.error_text
        assert not form.submit.disabled

    asyncio.run(scenario())


def test_commitment_double_tap_queues_one_save():
    page = Page()
    app = make_app(page)
    app.draft, app.commitments = {}, []
    screen = CommitmentsStep(page, app)
    screen.save_and(next_step=5)
    screen.save_and(next_step=5)
    assert len(page.tasks) == 1
    assert screen.submit.disabled


def test_options_cache_coalesces_requests_and_returns_independent_data():
    async def scenario():
        api = Api()
        api._request = AsyncMock(return_value={"income_categories": ["salary"]})
        first, second = await asyncio.gather(api.transaction_options(), api.transaction_options())
        first["income_categories"].append("changed")
        assert second == {"income_categories": ["salary"]}
        api._request.assert_awaited_once()
        await api.clear_token()
        await api.transaction_options()
        assert api._request.await_count == 2

    asyncio.run(scenario())


@pytest.mark.parametrize("raw", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_amounts_are_rejected(raw):
    with pytest.raises(ValueError):
        to_amount(raw)


def test_savings_milestone_uses_recorded_amounts_and_clamps_bar():
    progress = savings_progress({"target_amount": "1000", "saved_amount": "250",
                                 "progress_percentage": 25}, "ZAR")
    assert progress.controls[-1].value == "R 250 to your 50% milestone"
    complete = savings_progress({"target_amount": "1000", "saved_amount": "1100",
                                 "progress_percentage": 110}, "ZAR")
    assert complete.controls[0].content.value == 1
    assert "Goal reached" in complete.controls[-1].value


def test_visual_checkpoints_only_mark_recorded_progress_as_reached():
    progress = savings_progress({"target_amount": "1000", "saved_amount": "250",
                                 "progress_percentage": 25}, "ZAR")
    checkpoints = progress.controls[2].controls
    assert [point.label for point in checkpoints] == [
        "25% milestone, reached", "50% milestone, ahead",
        "75% milestone, ahead", "100% milestone, ahead",
    ]


@pytest.mark.parametrize("screen_type, endpoint", [
    (TransactionsScreen, "transactions"),
    (CashFlowScreen, "timeline"),
    (GoalsScreen, "goals"),
    (DashboardScreen, "overview"),
])
def test_failed_load_can_retry_and_removes_all_loading_feedback(screen_type, endpoint):
    async def scenario():
        page = Page()
        app = make_app(page)
        result = [] if endpoint == "goals" else {"currency": "ZAR"}
        fetch = AsyncMock(side_effect=[RuntimeError("Offline"), result])
        setattr(app.api, endpoint, fetch)
        if screen_type is DashboardScreen:
            app.api.timeline = AsyncMock(return_value={"events": []})
        screen = screen_type(page, app)
        await screen.load()
        assert screen.error
        assert not screen.loading
        assert not screen.refresh_bar.visible
        assert not screen.view_control.loading_state.skeleton.visible
        await screen.load()
        assert screen.error is None
        assert not screen.loading
        assert not screen.refresh_bar.visible

    asyncio.run(scenario())


def test_goal_response_from_previous_session_is_ignored():
    async def scenario():
        page = Page()
        app = make_app(page)
        app.session_revision = 0
        pending = asyncio.Future()

        async def goals():
            return await pending

        app.api.goals = goals
        screen = GoalsScreen(page, app)
        task = asyncio.create_task(screen.load())
        await asyncio.sleep(0)
        app.session_revision += 1
        pending.set_result([{"id": 99, "name": "Previous account"}])
        await task
        assert screen.goals == []

    asyncio.run(scenario())


def test_avatar_updates_when_account_arrives_and_opens_profile():
    app = make_app(Page())
    app.open_profile = AsyncMock()
    avatar = ProfileAvatar(app)
    assert isinstance(avatar.content.content, ft.Icon)
    app.overview["user"] = {"name": "Alex Morgan Smith"}
    avatar.before_update()
    assert avatar.content.content.value == "AS"
    avatar.on_click(None)
    assert app.page.tasks == [(app.open_profile, ())]
    assert initials({"user": {"name": "  Alex  "}}) == "A"
    assert initials({"user": {"email": "alex@example.com"}}) == "A"


def test_profile_loads_account_once_and_back_preserves_original_view():
    async def scenario():
        app = FlowShelterApp.__new__(FlowShelterApp)
        app.page = Page()
        original = SimpleNamespace(route="/goals", saved_scroll=120)
        app.page.views = [original]
        app.overview, app.profile_user, app.session_revision = {}, {}, 0
        app.api = SimpleNamespace(me=AsyncMock(return_value={
            "name": "Alex Smith", "email": "alex@example.com",
        }))
        await app.open_profile()
        await app.open_profile()
        assert [v.route for v in app.page.views] == ["/goals", "/profile"]
        assert app.profile_user["name"] == "Alex Smith"
        app.api.me.assert_awaited_once()
        app.close_profile()
        assert app.page.views == [original]
        assert original.saved_scroll == 120

    asyncio.run(scenario())


def test_profile_failure_can_retry_and_sign_out_is_guarded():
    async def scenario():
        page = Page()
        app = make_app(page)
        app.close_profile = lambda e=None: None
        app.session_revision = 0
        app.api.me = AsyncMock(side_effect=[RuntimeError("Offline"), {
            "name": "Alex", "email": "alex@example.com",
        }])
        screen = ProfileScreen(page, app)
        await screen.load()
        assert screen.error
        assert not screen.loading.visible
        await screen.load()
        assert screen.error is None
        assert screen.user["email"] == "alex@example.com"
        await screen._sign_out()
        await screen._sign_out()
        app.logout.assert_awaited_once()

    asyncio.run(scenario())
