def detect_language(message: str, explicit_language: str | None = None) -> str:
    if explicit_language:
        return explicit_language.lower()

    normalized = message.lower()
    if any(token in normalized for token in ("ano", "kailan", "magkano", "paki", "tagalog", "filipino")):
        return "fil"
    if any(token in normalized for token in ("unsa", "kanus-a", "palihug", "bisaya", "cebuano")):
        return "ceb"
    return "en"
