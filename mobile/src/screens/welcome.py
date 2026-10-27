"""Welcome screen — the first screen a user sees (design: screens/s1.png).

Holds the product promise, the language picker, and the two entry points into
authentication. Tapping "Create account" or "Log in" swaps the auth form in
below the copy instead of navigating away.
"""

from i18n import t
from i18n import LANGUAGES

import flet as ft

from theme import (
    BG,
    BODY_SM,
    CAPTION_SIZE,
    HEADING,
    INK,
    INPUT_SIZE,
    MUTED,
    PRIMARY,
    SPACE_M,
    TITLE_LG,
    primary_button,
    secondary_button,
    style_input,
)

from screens.auth import AuthPanel
from widgets import action_row

class WelcomeScreen:
    def __init__(self, page: ft.Page, app):
        self.page = page
        self.app = app

        self.language = style_input(
            ft.Dropdown(
                value="en",
                options=[
                    ft.DropdownOption(key=code, text=name)
                    for code, name in LANGUAGES.items()
                ],
                # Flet 1.x fires on_select (on_change does not exist here).
                on_select=self._language_changed,
            )
        )

        self.actions = action_row(
            primary_button(t('Create account'), lambda e: self.show_auth(register=True), expand=True),
            secondary_button(t('Log in'), lambda e: self.show_auth(register=False), expand=True),
        )

        self.form_slot = ft.Column(
            tight=True, spacing=SPACE_M, visible=False,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[],
        )

        self.brand_image = ft.Image(
            src="flowshelterlogo.png", width=240, height=160,
            fit=ft.BoxFit.CONTAIN,
        )
        self.intro = ft.Column(
            spacing=SPACE_M,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Text(
                    t('MONEY PLANNING FOR FREELANCERS'),
                    size=CAPTION_SIZE, weight=ft.FontWeight.W_600,
                    color=MUTED, text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            t('Plan for the days\n'),
                            style=ft.TextStyle(
                                color=PRIMARY,
                                italic=True,
                                weight=ft.FontWeight.W_700,
                            ),
                        ),
                        ft.TextSpan(
                            t('between paydays'),
                            style=ft.TextStyle(
                                color=PRIMARY,
                                italic=True,
                                weight=ft.FontWeight.W_700,
                            ),
                        ),
                    ],
                    size=TITLE_LG,
                    weight=ft.FontWeight.W_600, color=INK,
                    style=ft.TextStyle(height=1.2, letter_spacing=-0.6),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    t('Manage irregular income, cover essential bills, and save towards your goals with a clearer plan.'), size=INPUT_SIZE,
                    color=MUTED, text_align=ft.TextAlign.CENTER,
                ),
            ],
        )
        self.body = ft.Column(
            spacing=24,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.brand_image,
                            ft.Text(
                                "FlowShelter", size=HEADING,
                                weight=ft.FontWeight.W_700, color=PRIMARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                ),
                self.intro,
                ft.Column(
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        ft.Text(t('Language'), size=BODY_SM,
                                weight=ft.FontWeight.W_600, color=INK),
                        self.language,
                    ],
                ),
                self.actions,
                self.form_slot,
                ft.Text(
                    t('Your language preference is saved on this device.'),
                    size=CAPTION_SIZE, color=MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        )


    # ---- layout ----------------------------------------------------------
    def view(self) -> ft.View:
        return ft.View(
            route="/",
            padding=ft.Padding.symmetric(horizontal=24, vertical=32),
            bgcolor=BG,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[ft.Container(width=440, content=self.body)],
            scroll=ft.ScrollMode.AUTO,
        )

    def show_auth(self, register: bool):
        self.actions.visible = False
        self.intro.visible = False
        self.brand_image.width, self.brand_image.height = 180, 120
        self.form_slot.visible = True
        self.form_slot.controls = [AuthPanel(self.app, register)]
        self.page.update()

    def show_welcome(self):
        self.form_slot.controls = []
        self.actions.visible = True
        self.intro.visible = True
        self.brand_image.width, self.brand_image.height = 240, 160
        self.form_slot.visible = False
        self.page.update()

    # ---- language --------------------------------------------------------
    def _language_changed(self, e):
        self.app.set_language(self.language.value or "en")
        self.page.run_task(self.app.save_language, self.language.value or "en")
