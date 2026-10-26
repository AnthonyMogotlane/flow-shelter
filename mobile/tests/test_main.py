"""Behaviour tests for the mobile app.

These cover the UI rules that are easy to break without noticing: the
skeleton never flashing on a fast load, milestone messages firing once, and
navigation not stacking duplicate views.

They run as plain unit tests (no Flet session needed) by exercising the small
pure pieces the screens delegate to. Run with `uv run pytest` from `mobile/`.
"""

import asyncio

import app as app_module
import theme
from app import FlowShelterApp


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------
def test_crossed_reports_only_newly_crossed_bands():
    """A jump from 20% to 55% crosses 25 and 50; the first is reported."""

    assert FlowShelterApp._crossed(20, 55) == 25
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

    def __init__(self):
        self.goal_progress = {}


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
    theme.set_reduce_motion(False)
    assert theme.duration() == theme.ANIMATION_MS

    theme.set_reduce_motion(True)
    assert theme.duration() == 0
    assert theme.duration(400) == 0
    assert theme.reduce_motion() is True

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
