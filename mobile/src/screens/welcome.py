import flet as ft

# Palette — matches the app's existing colours in main.py.
BG = "#F5F7F2"
INK = "#1B2A23"
MUTED = "#64736A"
FIELD_BORDER = "#D5DCD5"
ERROR = "#B3261E"

LANGUAGES = {
    "en": "English",
    "zu": "isiZulu",
    "af": "Afrikaans",
    "xh": "isiXhosa",
    "st": "Sesotho",
}

LANGUAGE_PREF_KEY = "language"


async def _read_language(prefs: ft.SharedPreferences) -> str:
    saved = await prefs.get(LANGUAGE_PREF_KEY)
    return saved if saved in LANGUAGES else "en"


async def _save_language(prefs: ft.SharedPreferences, code: str) -> None:
    await prefs.set(LANGUAGE_PREF_KEY, code)


def _logo() -> ft.Row:
    """The small 'FS FlowShelter' wordmark in the top-left."""

    return ft.Row(
        spacing=6,
        controls=[
            ft.Container(
                content=ft.Text(
                    "FS",
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color=BG,
                ),
                bgcolor=INK,
                border_radius=3,
                width=18,
                height=18,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Text(
                "FlowShelter",
                size=14,
                weight=ft.FontWeight.W_600,
                color=INK,
            ),
        ],
    )


def _style_input(control: ft.Control) -> ft.Control:
    """Apply the shared outlined-input look to a TextField / Dropdown."""

    control.text_size = 15
    control.border = ft.OutlineInputBorder(
        border_radius=ft.BorderRadius.all(8),
        side=ft.BorderSide(1, FIELD_BORDER),
    )
    control.content_padding = ft.Padding.symmetric(horizontal=12, vertical=14)
    return control


def welcome_screen(page: ft.Page) -> ft.View:
    """Build the welcome view for `page`."""

    prefs = ft.SharedPreferences()

    # ---- Language -------------------------------------------------------
    language_dropdown = _style_input(
        ft.Dropdown(
            value="en",
            options=[
                ft.DropdownOption(key=code, text=name)
                for code, name in LANGUAGES.items()
            ],
        )
    )

    def on_language_change(e):
        page.run_task(_save_language, prefs, language_dropdown.value)

    language_dropdown.on_change = on_language_change

    # ---- Entry points ---------------------------------------------------
    create_account_button = ft.FilledButton(
        content="Create account",
        bgcolor=INK,
        color=BG,
        height=44,
        on_click=lambda e: show_mode(register=True),
    )
    login_button = ft.Container(
        content=ft.Button(
            content="Log in",
            color=INK,
            height=44,
            style=ft.ButtonStyle(
                bgcolor=BG,
                side=ft.BorderSide(1, FIELD_BORDER),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=lambda e: show_mode(register=False),
        ),
    )

    primary_actions = ft.Row(
        spacing=10,
        controls=[create_account_button, login_button],
    )

    # ---- Inline account form -------------------------------------------
    name_field = _style_input(
        ft.TextField(
            label="Name",
            capitalization=ft.TextCapitalization.WORDS,
        )
    )
    email_field = _style_input(
        ft.TextField(
            label="Email",
            keyboard_type=ft.KeyboardType.EMAIL,
        )
    )
    password_field = _style_input(
        ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
        )
    )
    auth_title = ft.Text(size=18, weight=ft.FontWeight.W_600, color=INK)
    auth_error = ft.Text(size=13, color=ERROR, visible=False)
    submit_button = ft.FilledButton(
        content="Create account",
        bgcolor=INK,
        color=BG,
        height=44,
        on_click=lambda e: on_submit(),
    )
    back_button = ft.TextButton(content="Back", on_click=lambda e: hide_form())

    account_form = ft.Column(
        tight=True,
        spacing=12,
        visible=False,
        controls=[
            auth_title,
            name_field,
            email_field,
            password_field,
            auth_error,
            ft.Row(spacing=10, controls=[submit_button, back_button]),
        ],
    )

    def show_mode(register: bool):
        """Swap the welcome buttons for the sign-up / log-in form."""

        account_form.visible = True
        name_field.visible = register
        password_field.hint_text = (
            "At least 12 characters" if register else "Your password"
        )
        auth_title.value = "Create your account" if register else "Welcome back"
        submit_button.content = "Create account" if register else "Log in"
        primary_actions.visible = False
        auth_error.visible = False
        page.update()

    def hide_form():
        account_form.visible = False
        primary_actions.visible = True
        page.update()

    def _show_error(message: str):
        auth_error.value = message
        auth_error.visible = True
        page.update()

    def on_submit():
        # Placeholder until the auth screens exist. The backend contract is:
        #   POST /auth/register {name, email, password} -> 201 user
        #     name 2-100 chars, password 12-128 chars (422 otherwise)
        #   POST /auth/login {email, password} -> 200 {access_token, token_type}
        #     and the token goes in "Authorization: Bearer <token>" afterwards.
        email = email_field.value.strip()
        password = password_field.value
        is_register = name_field.visible

        if is_register and len(name_field.value.strip()) < 2:
            return _show_error("Enter your name.")
        if not email:
            return _show_error("Enter your email address.")
        if is_register and len(password) < 12:
            return _show_error("Password must be at least 12 characters.")
        if not password:
            return _show_error("Enter your password.")

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Create account" if is_register else "Log in"),
                content=ft.Text(
                    "Sign-up and log-in screens are not built yet. "
                    "This form is ready to call the Flow Shelter API."
                ),
                actions=[
                    ft.TextButton(
                        content="OK",
                        on_click=lambda e: page.pop_dialog(),
                    )
                ],
            )
        )

    # Restore the saved language once it has been read from device storage.
    page.run_task(_read_language, prefs).add_done_callback(
        lambda f: _apply_language(language_dropdown, f.result(), page)
    )

    body = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            _logo(),
            ft.Container(expand=True),
            ft.Text(
                "MONEY PLANNING FOR FREELANCERS",
                size=11,
                weight=ft.FontWeight.W_600,
                color=MUTED,
            ),
            ft.Container(height=10),
            ft.Text(
                "Know what is safe to spend.",
                size=34,
                weight=ft.FontWeight.W_700,
                color=INK,
            ),
            ft.Container(height=8),
            ft.Text(
                "Plan around irregular income, essential bills and savings "
                "goals — without the guesswork.",
                size=15,
                color=MUTED,
            ),
            ft.Container(height=28),
            ft.Text("Language", size=13, weight=ft.FontWeight.W_600, color=INK),
            ft.Container(height=6),
            language_dropdown,
            ft.Container(height=16),
            primary_actions,
            account_form,
            ft.Container(height=12),
            ft.Text(
                "Your language preference is saved on this device.",
                size=11,
                color=MUTED,
            ),
            ft.Container(height=24),
        ],
    )

    return ft.View(
        route="/",
        padding=ft.Padding.symmetric(horizontal=24, vertical=16),
        bgcolor=BG,
        controls=[body],
    )


def _apply_language(dropdown: ft.Dropdown, code: str, page: ft.Page):
    dropdown.value = code
    page.update()
