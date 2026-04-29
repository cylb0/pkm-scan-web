from pydantic import BaseModel
from .languages import SupportedLanguage


class ImageTask(BaseModel):
    expansion: str
    lang: SupportedLanguage
    card_id: str
    s3_key: str
