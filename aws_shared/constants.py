from .languages import SupportedLanguage

FOLDER_RAW = "raw"
FOLDER_MEDIA = "media"
# FOLDER_SCANS = "scans" # For future usecase


def get_s3_img_key(
    folder: str, expansion: str, lang: SupportedLanguage, card_id: str, extension: str
) -> str:
    return f"{folder}/{expansion}/{lang.value}/{card_id}.{extension}"
