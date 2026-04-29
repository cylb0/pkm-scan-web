from enum import Enum

LANG_MAP = {
    "en": "English",
    "fr": "French",
    "jp": "Japanese",
}


class SupportedLanguage(str, Enum):
    EN = "en"
    FR = "fr"
    JP = "jp"

    @property
    def label(self) -> str:
        return LANG_MAP.get(self.value, self.name)

    @classmethod
    def to_choices(cls):
        return [(lang.value, lang.label) for lang in cls]
