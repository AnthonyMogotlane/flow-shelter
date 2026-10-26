"""Session-local UI translation. Only explicitly marked app copy is translated."""

from dataclasses import fields, is_dataclass
from functools import lru_cache
import re

from translations import CATALOGS

LANGUAGES = {"en": "English", "zu": "isiZulu", "af": "Afrikaans", "xh": "isiXhosa", "st": "Sesotho"}
LANGUAGE_PREF_KEY = "language"


def _session_language():
    try:
        import flet as ft
        return getattr(ft.context.page, "language_code", "en")
    except (RuntimeError, AttributeError):
        return "en"


class LocalizedText(str):
    def __new__(cls, source, params=None, language=None, transform=None):
        params = params or {}
        language = language or _session_language()
        template = CATALOGS.get(language, {}).get(source, source)
        values = {key: str(value.render(language)) if isinstance(value, LocalizedText)
                  else value for key, value in params.items()}
        text = template.format(**values) if values else template
        if transform:
            text = getattr(text, transform)()
        obj = super().__new__(cls, text)
        obj.source, obj.params, obj.transform = source, params, transform
        return obj

    def render(self, language):
        return LocalizedText(self.source, self.params, language, self.transform)

    def upper(self):
        return LocalizedText(self.source, self.params, transform="upper")

    def capitalize(self):
        return LocalizedText(self.source, self.params, transform="capitalize")

    def title(self):
        return LocalizedText(self.source, self.params, transform="title")

    def __add__(self, other):
        return t("{left}{right}", left=self, right=other)

    def __radd__(self, other):
        return t("{left}{right}", left=other, right=self)


def t(source, **params):
    if isinstance(source, LocalizedText) and not params:
        return source
    return LocalizedText(str(source), params)


def localize_tree(root, language):
    """Translate marked strings in place, preserving input values and control state."""
    seen = set()

    def visit(value):
        if isinstance(value, LocalizedText):
            return value.render(language)
        if isinstance(value, list):
            for index, item in enumerate(value):
                value[index] = visit(item)
        elif is_dataclass(value) and not isinstance(value, type):
            if id(value) in seen:
                return value
            seen.add(id(value))
            for field in fields(value):
                if field.name.startswith("_") or field.name in {"data", "key", "ref"}:
                    continue
                child = getattr(value, field.name, None)
                translated = visit(child)
                # Flet tracks property assignments; avoid dirtying unchanged controls.
                if isinstance(child, LocalizedText) and str(child) != str(translated):
                    setattr(value, field.name, translated)
        return value

    visit(root)


def install_localization(page):
    """Keep existing page.update calls and native dialogs locale-aware."""
    original_update, original_dialog = page.update, page.show_dialog

    def update(*controls, **kwargs):
        language = getattr(page, "language_code", "en")
        localize_tree(list(controls) if controls else page.views, language)
        dialogs = getattr(page, "_dialogs", None)
        if dialogs is not None:
            localize_tree(dialogs, language)
        return original_update(*controls, **kwargs)

    def show_dialog(dialog):
        localize_tree(dialog, getattr(page, "language_code", "en"))
        return original_dialog(dialog)

    page.update, page.show_dialog = update, show_dialog


def translated_server_text(value):
    """Known system labels only; never applied to a user's names or notes."""
    if not value or isinstance(value, LocalizedText):
        return value
    if value in CATALOGS["af"]:
        return t(value)
    for source, pattern in _server_patterns():
        matched = pattern.fullmatch(value)
        if matched:
            return t(source, **matched.groupdict())
    return value


@lru_cache(maxsize=1)
def _server_patterns():
    patterns = []
    # Match only machine-authored alert templates, not arbitrary sentences that
    # happen to contain words such as "of" or a user's goal name.
    sources = (
        "Your commitments ({v0}) are more than what you have available ({v1}).",
        "{v0} payment was due on {v1} but has not arrived.",
        "{v0} payment is still expected on {v1}.",
        "You reached your '{v0}' goal.",
        "'{v0}' is due in {v1} day(s) and nothing has been saved yet.",
    )
    for source in sources:
        pieces = re.split(r"(\{v\d+\})", source)
        pattern = "".join(
            f"(?P<{piece[1:-1]}>.+?)" if re.fullmatch(r"\{v\d+\}", piece)
            else re.escape(piece) for piece in pieces
        )
        patterns.append((source, re.compile(pattern)))
    return patterns
