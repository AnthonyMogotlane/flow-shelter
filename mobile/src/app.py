"""App controller: owns state, decides which screen is showing.

Flow
  start → saved token? ─no→ welcome ─auth→ onboarding or dashboard
                        └yes→ (onboarding complete?) → dashboard
                              (otherwise) → onboarding at the saved step
"""

from i18n import t
from i18n import LANGUAGES, LANGUAGE_PREF_KEY, install_localization, localize_tree

import asyncio
import inspect

import flet as ft

from api.client import Api, Unauthenticated, error_message
from screens.cashflow import CashFlowScreen
from screens.dashboard import DashboardScreen
from screens.goals import GoalsScreen
from screens.profile import ProfileScreen
from screens.onboarding import (
    BalanceStep,
    CommitmentsStep,
    IncomeStep,
    WorkStep,
    goal_form_view,
    starting_picture_view,
)
from screens.transactions import TransactionsScreen
from screens.welcome import WelcomeScreen
from theme import (
    BG,
    BODY,
    BUTTON_H,
    INK,
    MUTED,
    SPACE_L,
    SPACE_XL,
    SURFACE,
    TITLE,
    set_reduce_motion as theme_set_reduce_motion,
)
from widgets import chrome_theme, snack

# Bottom-bar tabs, in order. Overview is the dashboard itself.
TABS = ("overview", "cashflow", "transactions", "goals")

# SharedPreferences key for the reduced-motion setting ("1" / "0").
REDUCE_MOTION_KEY = "reduce_motion"

STEPS = {
    1: WorkStep,
    2: BalanceStep,
    3: IncomeStep,
    4: CommitmentsStep,
}

MAX_STEP = 5


class FlowShelterApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.language = "en"
        self._language_lock = asyncio.Lock()
        self.page.language_code = "en"
        install_localization(page)
        self.api = Api()

        # Server state, refreshed rather than mutated from the UI.
        self.draft: dict = {}
        self.commitments: list[dict] = []
        self.overview: dict = {}
        self.profile_user: dict = {}

        # True while re-entering a saved draft: the goal form then opens the
        # review instead of creating a goal.
        self.resuming = False

        # Tab-screen state, kept for the session so switching tabs back and
        # forth remembers the month/view the user was looking at. Dropped on
        # logout.
        self.tab_view: dict = {"cashflow": "until_next_payment", "cashflow_month": None}
        self.tx_filters: dict = {"kind": "all", "from_date": None, "month": None}

        # Set while a tab switch is in flight, so double-taps can't stack two
        # loads. Tabs never open the same screen twice.
        self.busy = False

        # Guards a fast double back-press from popping two views at once.
        self._popping = False

        # SharedPreferences is attached in start(), before the first screen
        # paints; None until then.
        self.prefs: ft.SharedPreferences | None = None

        # Last seen progress per goal, used to spot a goal crossing 25/50/75%
        # and show one milestone message — never a celebration on every open.
        self.goal_progress: dict = {}
        self.session_revision = 0
        self._onboarding_screens = {}

        self.welcome = WelcomeScreen(page, self)
        self.dashboard = DashboardScreen(page, self)
        self.cashflow = CashFlowScreen(page, self)
        self.transactions = TransactionsScreen(page, self)
        self.goals = GoalsScreen(page, self)

        self._configure_page()

    def _configure_page(self):
        self.page.title = "Flow Shelter"
        self.page.bgcolor = BG
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = chrome_theme()
        self.page.on_view_pop = self._on_view_pop
        self.page.window.width = 400
        self.page.window.height = 860
        self.page.window.min_width = 320

    # ---- startup ---------------------------------------------------------
    async def start(self):
        prefs = ft.SharedPreferences()
        self.prefs = prefs
        await self._load_display_prefs()
        await self.api.load_token(prefs)
        if not self.api.is_authenticated:
            self.show_welcome()
            return

        try:
            await self.reload_draft()
        except Unauthenticated:
            await self.api.clear_token()
            self.show_welcome()
            return
        except Exception as exc:  # noqa: BLE001 - offline start
            self.show_offline(error_message(exc))
            return

        if self.draft.get("is_complete"):
            await self.open_dashboard()
        else:
            # current_step is 1..5. A screen saves its own step when moving
            # on, so reopening resumes at the same screen, not the next one.
            self.show_step(self.draft.get("current_step") or 1, resume=True)

    async def _load_display_prefs(self):
        """Restore display settings before the first screen paints."""

        try:
            language = await self.prefs.get(LANGUAGE_PREF_KEY)
        except Exception:
            language = "en"
        self.set_language(language if language in LANGUAGES else "en")
        try:
            saved = await self.prefs.get(REDUCE_MOTION_KEY)
        except Exception:  # noqa: BLE001 - a fresh store has nothing saved
            saved = None
        theme_set_reduce_motion(saved == "1")
        self.page.theme = chrome_theme()

    def set_language(self, language):
        if language not in LANGUAGES:
            language = "en"
        self.language = language
        self.page.language_code = language
        # Flutter's native pickers fall back to English for locales not bundled
        # with Material; app-owned copy still uses the selected language.
        native = language if language in ("en", "af", "zu") else "en"
        self.page.locale_configuration = ft.LocaleConfiguration(
            supported_locales=[ft.Locale(language_code=code) for code in ("en", "af", "zu")],
            current_locale=ft.Locale(language_code=native),
        )
        if hasattr(self, "welcome"):
            self.welcome.language.value = language
            localize_tree(self.welcome.body, language)
        self.page.update()

    async def save_language(self, language):
        # Selection updates immediately in the UI. Serialize persistence so a
        # slower earlier selection cannot overwrite a more recent preference.
        async with self._language_lock:
            if language != self.language or self.prefs is None:
                return
            try:
                await self.prefs.set(LANGUAGE_PREF_KEY, language)
            except Exception:
                snack(self.page, t("Could not save your language preference. Try again."), kind="error")

    async def save_reduce_motion(self, value: bool):
        """Apply and persist the reduced-motion preference."""

        theme_set_reduce_motion(value)
        self.page.theme = chrome_theme()
        if self.prefs is not None:
            await self.prefs.set(REDUCE_MOTION_KEY, "1" if value else "0")

    # ---- navigation ------------------------------------------------------
    def show_welcome(self):
        self._reset_views()
        self.welcome.show_welcome()
        self.page.views.append(self.welcome.view())
        self.page.update()

    def show_auth(self, register: bool):
        self.welcome.show_auth(register)

    def show_step(self, step: int, resume: bool = False):
        step = max(1, min(step, MAX_STEP))
        self.resuming = resume
        if step == 5:
            self.page.run_task(self.show_goal_form)
            return
        screen = self._onboarding_screens.get(step)
        if screen is None:
            screen = STEPS[step](self.page, self)
            self._onboarding_screens[step] = screen
        self._replace_view(screen.view())

    async def show_goal_form(self):
        # Step 5 of onboarding: review what was just entered.
        view = goal_form_view(self.page, self)
        view.route = f"/onboarding/{MAX_STEP}"
        self._replace_view(view)

    async def show_starting_picture(self):
        try:
            self.overview = await self.api.overview()
        except Unauthenticated:
            await self.logout()
            return
        except Exception as exc:  # noqa: BLE001
            self.show_offline(error_message(exc))
            return
        self._replace_view(starting_picture_view(self.page, self, self.overview))

    async def open_dashboard(self):
        self._show_tab_screen(self.dashboard, "overview")
        self.busy = False
        try:
            await self.dashboard.load()
        except Unauthenticated:
            await self.logout()
            return

    async def open_tab(self, tab: str):
        """Switch bottom-bar tabs. Each screen re-fetches when opened.

        Re-selecting the tab that is already showing does nothing, and a tap
        that arrives while the previous switch is still loading is dropped,
        so a double-tap can never fire two loads.
        """
        if tab not in TABS or self.busy:
            return
        current = self._current_view()
        if current is not None and getattr(current, "route", None) == f"/{tab}":
            return
        self.busy = True
        try:
            await self._open_screen(tab)
        finally:
            self.busy = False

    async def _open_screen(self, tab: str):
        if tab == "overview":
            await self.open_dashboard()
            return
        screen = self.tab_screen(tab)
        self._show_tab_screen(screen, tab)
        self.busy = False
        try:
            await screen.load()
        except Unauthenticated:
            await self.logout()
            return

    @staticmethod
    def _has_content(screen) -> bool:
        return bool(getattr(screen, "content", None) and screen.content.controls)

    def _show_tab_screen(self, screen, tab: str):
        """Put a tab screen on the stack without stacking duplicates.

        Switching between tabs replaces the top view (the nav is the only
        way back to another tab). Leaving a form lands on its tab: if that
        tab is already underneath, the form is popped so back returns to it;
        otherwise the form is replaced. Either way the stack never grows by
        switching tabs, so back always has somewhere to go.
        """
        views = self.page.views
        top = self._current_view()
        view = screen.view()

        if top is not None and getattr(top, "is_form", False):
            below = views[-2] if len(views) >= 2 else None
            if below is not None and getattr(below, "route", None) == view.route:
                # The tab is already underneath, so pop the form rather than
                # swapping in a fresh copy that loses its history.
                del views[-1]
                self.page.update()
                return

        replacement = top is not None and getattr(top, "route", "").startswith("/")
        if replacement:
            del views[-1]
        self.page.views.append(view)
        self.page.update()

    def tab_screen(self, tab: str):
        return {
            "cashflow": self.cashflow,
            "transactions": self.transactions,
            "goals": self.goals,
        }[tab]

    async def open_transaction_form(self, transaction: dict | None = None):
        """Add (transaction=None) or edit an existing transaction."""
        top = self._current_view()
        if top is not None and getattr(top, "is_form", False):
            return
        form = self.tab_screen("transactions").form(transaction)
        self._push_form(form.view())

    async def open_profile(self):
        top = self._current_view()
        if top is not None and top.route == "/profile":
            return
        screen = ProfileScreen(self.page, self)
        self._push(screen.view())
        await screen.load()

    def close_profile(self, e=None):
        top = self._current_view()
        if top is not None and top.route == "/profile" and len(self.page.views) > 1:
            self.page.views.pop()
            self.page.update()

    async def open_goal_form(self, goal: dict | None = None):
        top = self._current_view()
        if top is not None and getattr(top, "is_form", False):
            return
        form = self.tab_screen("goals").form(goal)
        self._push_form(form.view())

    def _push_form(self, view: ft.View):
        """Forms are marked so tab switching knows to return to their tab."""

        view.is_form = True  # type: ignore[attr-defined]
        self._push(view)

    # ---- back navigation -------------------------------------------------
    def _current_view(self) -> ft.View | None:
        return self.page.views[-1] if self.page.views else None

    def _on_view_pop(self, e: ft.ViewPopEvent):
        """System / browser back: drop the top view and show the one below."""

        # A fast double-press can deliver two pops before the first redraw;
        # one is enough, and popping twice would skip a screen.
        if self._popping:
            return
        views = self.page.views
        top = self._current_view()
        if top is None:
            return
        leave = getattr(top, "request_leave", None)
        if leave is not None:
            leave()
            return
        if len(views) == 1:
            # Nothing to return to (the welcome or offline screen): keep it.
            return
        self._popping = True
        try:
            del views[-1]
            self.page.update()
        finally:
            self._popping = False

    async def on_authenticated(self):
        await self.start()

    async def logout(self):
        self.session_revision += 1
        await self.api.clear_token()
        self.draft = {}
        self.commitments = []
        self.overview = {}
        self.profile_user = {}
        self.goal_progress = {}
        self._onboarding_screens = {}
        self.dashboard.series = []
        self.dashboard.error = None
        self.dashboard.chart_error = False
        self.cashflow.data = {}
        self.transactions.data = {}
        self.goals.goals = []
        for screen in (self.dashboard, self.cashflow, self.transactions, self.goals):
            screen.content.controls = []
            screen.loading = False
            screen.view_control.loading_state.finish()
            screen.refresh_bar.visible = False
            if hasattr(screen, "requests"):
                screen.requests.revision += 1
                screen.requests.pending.clear()
        self.tab_view = {"cashflow": "until_next_payment", "cashflow_month": None}
        self.tx_filters = {"kind": "all", "from_date": None, "month": None}
        self.show_welcome()

    # ---- engagement ------------------------------------------------------
    # Milestones are crossed at 25/50/75/100% of a goal. We compare against
    # the progress seen last time this session and speak up only when a goal
    # moves up a band, so reopening a screen never re-celebrates.
    MILESTONES = (100, 75, 50, 25)

    def note_goal_progress(self, goals) -> None:
        """Record each goal's progress and speak up when one crosses a band.

        At most one message is shown per call (the last goal that crossed),
        because stacking snackbars would bury the screen the user just
        opened.
        """

        message = None
        for goal in goals or []:
            goal_id = goal.get("id")
            if goal_id is None:
                continue
            progress = float(goal.get("progress_percentage") or 0)
            previous = self.goal_progress.get(goal_id)
            self.goal_progress[goal_id] = progress
            if previous is None:
                # First sighting this session: learn the baseline silently.
                continue
            crossed = self._crossed(previous, progress)
            if crossed is None:
                continue
            name = goal.get("name") or t("your goal")
            message = (
                t('You reached {v0}!', v0=name)
                if crossed == 100
                else t('{v0} is {v1}% funded. Keep going.', v0=name, v1=crossed)
            )
        if message:
            snack(self.page, message, kind="success")

    @classmethod
    def _crossed(cls, previous: float, current: float) -> int | None:
        for milestone in cls.MILESTONES:
            if previous < milestone <= current:
                return milestone
        return None

    # ---- data ------------------------------------------------------------
    async def reload_draft(self):
        self.draft = await self.api.get_onboarding()
        data = await self.api.get_commitments()
        self.commitments = data.get("commitments") or []

    async def start_onboarding(self):
        """Re-enter onboarding from the dashboard at the first step."""
        try:
            await self.reload_draft()
        except Unauthenticated:
            await self.logout()
            return
        except Exception as exc:  # noqa: BLE001
            self.show_offline(error_message(exc))
            return
        self._onboarding_screens = {}
        self.show_step(1)

    # ---- view helpers ----------------------------------------------------
    def _reset_views(self):
        self.page.views.clear()

    def _push(self, view: ft.View):
        """Append a view and show it.

        Flet refuses two views with the same route on the stack, and a form
        opened from a form would otherwise collide (e.g. a goal form opened
        while the onboarding goal form is still underneath). Only the case
        where the *top* view already holds that route needs a unique route,
        and it carries the tab's name so tab switching still recognises it.
        """

        top = self._current_view()
        route = getattr(view, "route", None)
        if top is not None and route and getattr(top, "route", None) == route:
            view.route = f"{route}/{id(view)}"
        self.page.views.append(view)
        self.page.update()

    def _replace_view(self, view: ft.View):
        """Go to a view, keeping a single back target underneath.

        The back button returns to the last tab when there is a dashboard
        underneath; otherwise the new view replaces the top one, so the
        hardware back button on Android leaves the app rather than landing
        on a stale step of onboarding.
        """

        run_after = getattr(view, "after_show", None)
        views = self.page.views
        top = self._current_view()
        on_tab = top is not None and getattr(top, "route", None) in {
            f"/{tab}" for tab in TABS
        }
        if on_tab or not views:
            self._push(view)
        else:
            del views[-1]
            self.page.views.append(view)
            self.page.update()

        if run_after is not None:
            task = run_after()
            if inspect.isawaitable(task):
                create = getattr(self.page, "run_task", None) or asyncio.create_task
                create(task)

    def show_offline(self, message: str):
        self._reset_views()
        self.page.views.append(
            ft.View(
                route="/offline",
                bgcolor=BG,
                padding=SPACE_XL,
                controls=[
                    ft.Container(expand=True),
                    ft.Text(
                        t("Can't load your plan"),
                        size=TITLE,
                        weight=ft.FontWeight.W_700,
                        color=INK,
                    ),
                    ft.Text(message, size=BODY, color=MUTED),
                    ft.Container(height=SPACE_L),
                    ft.FilledButton(
                        content=t("Try again"),
                        bgcolor=INK,
                        color=SURFACE,
                        height=BUTTON_H,
                        on_click=lambda e: self.page.run_task(self.start),
                    ),
                    ft.Container(expand=True),
                ],
            )
        )
        self.page.update()


def main(page: ft.Page):
    # main.py is the entry point; keep startup here so `flet run src/app.py`
    # behaves the same way.
    app = FlowShelterApp(page)
    page.run_task(app.start)


if __name__ == "__main__":
    ft.run(main)
