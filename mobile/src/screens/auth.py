"""Sign up / log in on top of the welcome screen.

Wireframe s1.png shows the welcome content with two buttons. Tapping either
swaps in the matching form here, which talks to /auth/register and
/auth/login. On success `app.on_authenticated()` decides the next screen.
"""

from i18n import t

import flet as ft

from theme import (
    INK,
    SPACE_M,
    SPACE_S,
    SUBHEAD,
    secondary_button,
    style_input,
    text_button,
)

from api.client import error_message
from widgets import error_text, set_busy, set_error, submit_button

MIN_PASSWORD = 12


class AuthPanel(ft.Column):
    """The form swapped into the welcome screen."""

    def __init__(self, app, register: bool):
        self.app = app
        self.register = register
        self.busy = False

        self.name = style_input(
            ft.TextField(
                label=t('Name'),
                capitalization=ft.TextCapitalization.WORDS,
                autofocus=True,
            )
        )
        self.email = style_input(
            ft.TextField(label=t('Email'), keyboard_type=ft.KeyboardType.EMAIL,
                         autofocus=not register)
        )
        self.password = style_input(
            ft.TextField(
                label=t('Password'),
                hint_text=t('At least {v0} characters', v0=MIN_PASSWORD),
                password=True,
                can_reveal_password=True,
                on_submit=lambda e: self._submit(),
            )
        )
        self.error = error_text()
        self.submit = submit_button(
            t('Create account') if register else t('Log in'),
            lambda e: self._submit(),
        )

        super().__init__(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=SPACE_M,
            controls=[
                ft.Text(
                    t('Create your account') if register else t('Welcome back'),
                    size=SUBHEAD,
                    weight=ft.FontWeight.W_600,
                    color=INK,
                    text_align=ft.TextAlign.CENTER,
                ),
                *([self.name] if register else []),
                self.email,
                self.password,
                self.error,
                ft.Row(
                    spacing=SPACE_S,
                    controls=[
                        secondary_button(
                            t('Back'), lambda e: self.app.show_welcome(), expand=True
                        ),
                        self.submit,
                    ],
                ),
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=text_button(
                            t('Already have an account? Log in')
                            if register
                            else t('New here? Create an account'),
                            lambda e: self.app.show_auth(not register),
                        ),
                ),
            ],
        )

    def _validate(self) -> str | None:
        name = (self.name.value or "").strip()
        email = (self.email.value or "").strip()
        password = self.password.value or ""
        self.name.error_text = self.email.error_text = self.password.error_text = None
        if self.register and len(name) < 2:
            self.name.error_text = t('Enter your name.')
            return t('Enter your name.')
        if "@" not in email or "." not in email.split("@")[-1]:
            self.email.error_text = t('Enter a valid email address.')
            return t('Enter a valid email address.')
        if self.register and len(password) < MIN_PASSWORD:
            self.password.error_text = t('Use at least {v0} characters.', v0=MIN_PASSWORD)
            return t('Password must be at least {v0} characters.', v0=MIN_PASSWORD)
        if not password:
            self.password.error_text = t('Enter your password.')
            return t('Enter your password.')
        return None

    def _submit(self):
        if self.busy:
            return
        problem = self._validate()
        if problem:
            set_error(self.error, problem, self.app.page)
            return

        set_error(self.error, None, self.app.page)
        self.busy = True
        set_busy(
            self.submit,
            True,
            t('Creating account') if self.register else t('Signing in'),
        )
        self.app.page.update()
        self.app.page.run_task(self._call_api)

    async def _call_api(self):
        try:
            if self.register:
                await self.app.api.register(
                    self.name.value.strip(),
                    self.email.value.strip().lower(),
                    self.password.value,
                )
            await self.app.api.login(
                self.email.value.strip().lower(), self.password.value
            )
        except Exception as exc:  # noqa: BLE001 - surfaced to the user
            set_error(self.error, error_message(exc), self.app.page)
            self.busy = False
            set_busy(self.submit, False)
            self.app.page.update()
            return

        try:
            await self.app.on_authenticated()
        finally:
            self.busy = False
            set_busy(self.submit, False)
