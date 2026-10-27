"""Compact account screen using the existing authenticated profile endpoint."""

from i18n import t
from i18n import LANGUAGES

import flet as ft

from api.client import Unauthenticated, error_message
from theme import (
    BODY, HEADING, INK, MINT, MUTED, PRIMARY, SPACE_L,
    SPACE_S, TITLE, style_input,
)
from widgets import (
    account_user, card, error_card, initials, padded, refresh_indicator,
    set_busy, submit_button, tab_view,
)


class ProfileScreen:
    def __init__(self, page, app):
        self.page, self.app = page, app
        self.user = dict(account_user(app))
        self.error = None
        self.loading = refresh_indicator()
        self.language = style_input(ft.Dropdown(
            label=t("Language"), value=getattr(app, "language", "en"),
            options=[ft.DropdownOption(key=code, text=name) for code, name in LANGUAGES.items()],
            on_select=self._change_language,
        ))
        self.sign_out = submit_button(t('Sign out'), lambda e: page.run_task(self._sign_out))
        self.content = ft.Column(
            spacing=SPACE_L, horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        self.view_control = tab_view(
            t('Profile'), app, padded(self.content), active="overview", route="/profile",
            on_back=app.close_profile,
        )
        self.render()

    def view(self):
        return self.view_control

    def render(self):
        letters = initials({"user": self.user})
        identity = ft.Column(
            spacing=SPACE_S, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=80, height=80, border_radius=40, bgcolor=MINT,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(letters, size=TITLE, color=PRIMARY,
                                    weight=ft.FontWeight.W_600)
                    if letters else ft.Icon(ft.Icons.PERSON_OUTLINE, size=32, color=PRIMARY),
                ),
                ft.Text(self.user.get("name") or t('Your profile'), size=HEADING,
                        weight=ft.FontWeight.W_600, color=INK, text_align=ft.TextAlign.CENTER),
            ],
        )
        details = []
        if self.user.get("email"):
            details.extend([
                ft.Text(t('Email'), size=BODY, color=MUTED),
                ft.Text(self.user["email"], size=BODY, color=INK, selectable=True),
            ])
        currency = (self.app.overview or {}).get("currency")
        if currency:
            details.extend([
                ft.Text(t('Plan currency'), size=BODY, color=MUTED),
                ft.Text(currency, size=BODY, color=INK),
            ])
        controls = [self.loading, card(identity, padding=SPACE_L)]
        if details:
            controls.append(card(ft.Column(spacing=SPACE_S, controls=details)))
        if self.error:
            controls.append(error_card(self.error, on_retry=lambda e: self.page.run_task(self.load)))
        controls.extend([self.language, self.sign_out])
        self.content.controls = controls

    def _change_language(self, e):
        self.app.set_language(self.language.value or "en")
        self.page.run_task(self.app.save_language, self.language.value or "en")

    async def load(self):
        if self.loading.visible or (self.user.get("name") and self.user.get("email")):
            return
        session = self.app.session_revision
        self.loading.visible = True
        self.error = None
        self.render()
        self.page.update()
        try:
            user = await self.app.api.me()
            if session != self.app.session_revision:
                return
            self.user = user
            self.app.profile_user = user
        except Unauthenticated:
            await self.app.logout()
            return
        except Exception as exc:
            self.error = error_message(exc)
        finally:
            self.loading.visible = False
        self.render()
        self.page.update()

    async def _sign_out(self):
        if self.sign_out.disabled:
            return
        set_busy(self.sign_out, True, t('Signing out'))
        self.page.update()
        try:
            await self.app.logout()
        except Exception as exc:
            self.error = error_message(exc)
            set_busy(self.sign_out, False)
            self.render()
            self.page.update()
