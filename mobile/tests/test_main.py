"""Behaviour tests for the mobile app.

These cover the UI rules that are easy to break without noticing: the
skeleton never flashing on a fast load, milestone messages firing once, and
navigation not stacking duplicate views.

They run as plain unit tests (no Flet session needed) by exercising the small
pure pieces the screens delegate to. Run with `uv run pytest` from `mobile/`.
"""

import asyncio
from types import SimpleNamespace

import app as app_module
import flet as ft
import theme
from app import FlowShelterApp


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------
def test_crossed_reports_only_newly_crossed_bands():
    """A jump across multiple bands reports the highest newly reached one."""

    assert FlowShelterApp._crossed(20, 55) == 50
    assert FlowShelterApp._crossed(26, 55) == 50
    assert FlowShelterApp._crossed(60, 80) == 75
    assert FlowShelterApp._crossed(80, 100) == 100


def test_crossed_is_silent_when_no_band_is_passed():
    assert FlowShelterApp._crossed(51, 74) is None
    assert FlowShelterApp._crossed(100, 100) is None
    # A goal edited back down is not a milestone.
    assert FlowShelterApp._crossed(60, 30) is None


class _FakeApp:
    """Just enough of the app for `note_goal_progress` to run."""

    MILESTONES = FlowShelterApp.MILESTONES
    _crossed = FlowShelterApp._crossed
    note_goal_progress = FlowShelterApp.note_goal_progress

    def __init__(self):
        self.goal_progress = {}
        self.page = object()


def _run_note_progress(progress_values):
    """Feed a goal's progress through `note_goal_progress` and return what
    the user would have been told, in order."""

    spoken = []
    original = app_module.snack
    app_module.snack = lambda page, msg, kind="success": spoken.append(msg)
    try:
        fake = _FakeApp()
        for progress in progress_values:
            fake.note_goal_progress(
                [{"id": 1, "name": "Tax", "progress_percentage": progress}]
            )
    finally:
        app_module.snack = original
    return spoken


def test_first_sighting_learns_the_baseline_without_celebrating():
    """Opening a screen must not celebrate progress that already existed."""

    # 80% on first sight teaches the baseline silently; dropping to 60% is
    # not a milestone; 100% is the one message we want.
    assert _run_note_progress([80, 60, 100]) == ["You reached Tax!"]


def test_crossing_one_band_at_a_time_speaks_once_each():
    assert _run_note_progress([10, 30, 55, 80]) == [
        "Tax is 25% funded. Keep going.",
        "Tax is 50% funded. Keep going.",
        "Tax is 75% funded. Keep going.",
    ]


# ---------------------------------------------------------------------------
# Reduced motion
# ---------------------------------------------------------------------------
def test_reduced_motion_zeroes_every_animation():
    from widgets import chrome_theme

    theme.set_reduce_motion(False)
    assert theme.duration() == theme.ANIMATION_MS
    assert (
        chrome_theme().page_transitions.windows
        == ft.PageTransitionTheme.ZOOM
    )

    theme.set_reduce_motion(True)
    assert theme.duration() == 0
    assert theme.duration(400) == 0
    assert theme.reduce_motion() is True
    assert (
        chrome_theme().page_transitions.windows
        == ft.PageTransitionTheme.NONE
    )

    # Always restore: this is module state shared by every test.
    theme.set_reduce_motion(False)


# ---------------------------------------------------------------------------
# Loading placeholder
# ---------------------------------------------------------------------------
class _FakeSkeleton:
    def __init__(self):
        self.visible = False


class _FakePage:
    def __init__(self):
        self.tasks = []
        self.updated = []
        self.views = []

    def run_task(self, handler, *args):
        self.tasks.append((handler, args))

    def update(self, *controls):
        self.updated.extend(controls)


def test_loading_state_shows_skeleton_only_when_the_load_is_slow():
    from widgets import LoadingState

    page = _FakePage()
    skeleton = _FakeSkeleton()
    state = LoadingState(page, skeleton, delay_ms=50_000)

    state.start()
    # Nothing painted yet: the delay has not elapsed.
    assert skeleton.visible is False

    state.finish()  # the request came back first
    assert skeleton.visible is False


def test_loading_state_waits_then_reveals():
    from widgets import LoadingState

    async def scenario():
        page = _FakePage()
        skeleton = _FakeSkeleton()
        state = LoadingState(page, skeleton, delay_ms=1)
        state.start()
        handler, args = page.tasks.pop(0)
        await handler(*args)
        return skeleton.visible

    assert asyncio.run(scenario()) is True


def test_loading_state_finish_cancels_a_pending_reveal():
    from widgets import LoadingState

    async def scenario():
        page = _FakePage()
        skeleton = _FakeSkeleton()
        state = LoadingState(page, skeleton, delay_ms=1)
        state.start()
        state.finish()
        handler, args = page.tasks.pop(0)
        await handler(*args)
        return skeleton.visible

    assert asyncio.run(scenario()) is False


# ---------------------------------------------------------------------------
# Navigation and interaction feedback
# ---------------------------------------------------------------------------
class _FakeScreen:
    def __init__(self, route):
        self.route = route

    def view(self):
        return SimpleNamespace(route=self.route)


def test_tab_switch_replaces_the_top_view_without_growing_the_stack():
    app = FlowShelterApp.__new__(FlowShelterApp)
    app.page = _FakePage()
    app.page.views = [SimpleNamespace(route="/overview")]

    FlowShelterApp._show_tab_screen(app, _FakeScreen("/cashflow"), "cashflow")
    FlowShelterApp._show_tab_screen(app, _FakeScreen("/goals"), "goals")

    assert [view.route for view in app.page.views] == ["/goals"]


def test_returning_to_tab_under_a_form_preserves_the_tab_view():
    app = FlowShelterApp.__new__(FlowShelterApp)
    app.page = _FakePage()
    tab = SimpleNamespace(route="/goals")
    form = SimpleNamespace(route="/goals/form", is_form=True)
    app.page.views = [tab, form]

    FlowShelterApp._show_tab_screen(app, _FakeScreen("/goals"), "goals")

    assert app.page.views == [tab]


def test_submit_button_shows_and_restores_busy_feedback():
    from widgets import set_busy, submit_button

    button = submit_button("Save", on_click=lambda e: None)
    set_busy(button, True, "Signing in")

    assert button.disabled is True
    assert isinstance(button.content, ft.Semantics)
    assert button.content.label == "Signing in"
    assert isinstance(button.content.content.controls[0], ft.ProgressRing)

    set_busy(button, False)

    assert button.disabled is False
    assert isinstance(button.content, ft.Text)
    assert button.content.value == "Save"


def test_segmented_filters_use_a_native_single_choice_control():
    from types import SimpleNamespace

    from theme import BUTTON_H
    from widgets import segmented

    selected = []
    control = segmented(
        [("all", "All"), ("income", "Income")],
        "all",
        on_select=selected.append,
    )

    assert isinstance(control, ft.Container)
    assert control.width == float("inf")
    assert control.height == BUTTON_H

    segments = control.content.controls
    first, divider, second = segments
    assert isinstance(first, ft.Semantics)
    assert isinstance(second, ft.Semantics)
    assert isinstance(divider, ft.Container)
    assert first.content.height == control.height
    assert second.content.height == control.height
    assert first.content.expand is True
    assert second.content.expand is True
    assert first.selected is True
    assert second.selected is False

    first.content.on_click(SimpleNamespace(control=SimpleNamespace(page=None)))

    assert selected == ["all"]
    assert first.selected is True
    assert second.selected is False


def test_tappable_cards_expose_an_accessible_button_name():
    from widgets import tappable

    control = tappable(
        ft.Container(content=ft.Text("Tax")),
        on_click=lambda e: None,
        label="Open savings goal Tax",
    )

    assert isinstance(control, ft.Semantics)
    assert control.label == "Open savings goal Tax"
    assert control.button is True
    assert control.focusable is True


def test_error_card_retry_action_calls_its_handler():
    from widgets import error_card

    retries = []
    control = error_card(
        "Could not load goals.",
        on_retry=lambda e: retries.append(True),
    )
    retry_button = control.content.controls[1]

    assert retry_button.content.value == "Try again"
    retry_button.on_click(None)
    assert retries == [True]
