"""Language changes must translate UI without changing data or API values."""

import ast
import asyncio
from pathlib import Path
from string import Formatter
from types import SimpleNamespace

import flet as ft
import pytest

from app import FlowShelterApp
from i18n import LANGUAGES, LocalizedText, install_localization, localize_tree, t, translated_server_text
from translations import CATALOGS


class Page:
    def __init__(self):
        self.views = []
        self.window = SimpleNamespace()
        self.updated = 0
        self.dialogs = []
        self.tasks = []

    def update(self, *controls, **kwargs):
        self.updated += 1

    def show_dialog(self, dialog):
        self.dialogs.append(dialog)

    def run_task(self, handler, *args):
        self.tasks.append((handler, args))


def text_values(root):
    from dataclasses import fields, is_dataclass
    values, seen = [], set()

    def visit(item):
        if isinstance(item, str):
            values.append(str(item))
        elif isinstance(item, list):
            for child in item:
                visit(child)
        elif is_dataclass(item) and id(item) not in seen:
            seen.add(id(item))
            for field in fields(item):
                if not field.name.startswith("_") and field.name not in ("data", "key", "ref"):
                    visit(getattr(item, field.name, None))

    visit(root)
    return values


@pytest.mark.parametrize("language", list(LANGUAGES))
def test_switching_language_preserves_input_and_dropdown_keys(language):
    field = ft.TextField(label=t("Name"), value="Income {Alex}")
    option = ft.DropdownOption(key="income", text=t("Income"))
    select = ft.Dropdown(value="income", options=[option])
    root = ft.Column(controls=[field, select, ft.Text(t("Transactions"))])
    localize_tree(root, language)
    expected = "Name" if language == "en" else CATALOGS[language]["Name"]
    assert field.label == expected
    assert field.value == "Income {Alex}"
    assert option.key == select.value == "income"
    localize_tree(root, "en")
    assert field.label == "Name"
    assert option.text == "Income"


def test_templates_keep_user_names_and_real_amounts_unchanged():
    name = "Saved {do not format}"
    text = t("{v0} is {v1}% funded. Keep going.", v0=name, v1=25)
    translated = text.render("af")
    assert name in translated
    assert "25%" in translated
    assert translated.source == text.source
    assert translated.render("en") == f"{name} is 25% funded. Keep going."


def test_nested_greeting_and_headline_spans_roundtrip():
    greeting = ft.Text(t("{v0}, {v1}", v0=t("Good morning"), v1="Alex"))
    headline = ft.Text(spans=[ft.TextSpan(t("Plan for the days\n")),
                              ft.TextSpan(t("between paydays"))])
    root = ft.Column(controls=[greeting, headline])
    localize_tree(root, "af")
    assert greeting.value == "Goeiemôre, Alex"
    assert headline.spans[1].text == "tussen betaaldae"
    localize_tree(root, "en")
    assert greeting.value == "Good morning, Alex"
    assert headline.spans[0].text == "Plan for the days\n"


def test_two_pages_keep_independent_languages_and_dialogs_translate():
    first, second = Page(), Page()
    for page, code in ((first, "af"), (second, "zu")):
        page.language_code = code
        page.views = [ft.View(controls=[ft.Text(t("Transactions"))])]
        install_localization(page)
        page.update()
    assert first.views[0].controls[0].value == "Transaksies"
    assert second.views[0].controls[0].value == "Ukuthengiselana"
    first.update()
    assert first.views[0].controls[0].value == "Transaksies"
    dialog = ft.AlertDialog(title=ft.Text(t("Discard your changes?")))
    second.show_dialog(dialog)
    assert dialog.title.value == CATALOGS["zu"]["Discard your changes?"]


def test_language_preference_restores_and_existing_form_values_survive():
    async def scenario():
        stored = {}

        class Prefs:
            async def get(self, key):
                return stored.get(key)

            async def set(self, key, value):
                stored[key] = value

        app = FlowShelterApp(Page())
        app.prefs = Prefs()
        app.show_welcome()
        app.show_auth(register=True)
        panel = app.welcome.form_slot.controls[0]
        panel.name.value = "My own name"
        panel.email.value = "alex@example.com"
        app.set_language("st")
        await app.save_language("st")
        assert app.welcome.form_slot.controls[0] is panel
        assert panel.name.value == "My own name"
        assert panel.email.value == "alex@example.com"
        assert panel.submit.content.value == CATALOGS["st"]["Create account"]
        assert stored["language"] == "st"
        reopened = FlowShelterApp(Page())
        reopened.prefs = Prefs()
        await reopened._load_display_prefs()
        assert reopened.language == "st"
        assert reopened.welcome.language.value == "st"
        assert CATALOGS["st"]["between paydays"] in text_values(reopened.welcome.body)
        reopened.set_language("unsupported")
        assert reopened.language == "en"

    asyncio.run(scenario())


def test_rapid_language_changes_persist_the_latest_selection():
    async def scenario():
        app = FlowShelterApp(Page())
        stored = {}
        first_write = asyncio.Event()
        finish_first = asyncio.Event()

        class Prefs:
            async def set(self, key, value):
                if value == "zu":
                    first_write.set()
                    await finish_first.wait()
                stored[key] = value

        app.prefs = Prefs()
        app.set_language("zu")
        first = asyncio.create_task(app.save_language("zu"))
        await first_write.wait()
        app.set_language("af")
        second = asyncio.create_task(app.save_language("af"))
        finish_first.set()
        await asyncio.gather(first, second)
        await app.save_language("zu")  # a queued obsolete event is ignored
        assert app.language == stored["language"] == "af"

    asyncio.run(scenario())


def test_known_server_alerts_translate_but_unknown_content_is_preserved():
    text = translated_server_text("You reached your 'Travel {2026}' goal.")
    assert isinstance(text, LocalizedText)
    assert "Travel {2026}" in text.render("af")
    assert "bereik" in text.render("af")
    assert translated_server_text("My personal note") == "My personal note"


def test_translated_strings_use_flets_native_transport():
    import msgpack
    from flet.controls.base_control import BaseControl
    from flet.messaging.protocol import configure_encode_object_for_msgpack

    control = ft.Text(t("Transactions"))
    localize_tree(control, "af")
    encoded = msgpack.packb(control, default=configure_encode_object_for_msgpack(BaseControl))
    assert msgpack.unpackb(encoded)["value"] == "Transaksies"


def test_all_translation_templates_keep_the_same_placeholders():
    def placeholders(text):
        return {field for _, field, _, _ in Formatter().parse(text) if field}

    for language, catalog in CATALOGS.items():
        assert len(catalog) > 250
        for source, translated in catalog.items():
            assert translated.strip(), (language, source)
            assert placeholders(source) == placeholders(translated), (language, source)


def test_all_explicit_interface_copy_has_catalog_entries():
    root = Path(__file__).resolve().parents[1] / "src"
    brand = {"FS", "FlowShelter", "FLOWSHELTER"}
    missing = set()
    for path in root.rglob("*.py"):
        if path.name in ("translations.py", "i18n.py"):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "t" and node.args
                    and isinstance(node.args[0], ast.Constant)):
                continue
            source = node.args[0].value
            # Templates composed entirely of runtime values need no word translation.
            literal = "".join(part for part, _, _, _ in Formatter().parse(source))
            if source not in brand and any(c.isalpha() for c in literal):
                for catalog in CATALOGS.values():
                    if source not in catalog:
                        missing.add(source)
    assert missing == set()
