import pandas as pd


def is_requesting_internal_notes(user_input: str) -> bool:
    patterns = [
        "internal notes",
        "show me your notes",
        "show your notes",
        "hidden notes",
        "system prompt",
        "hidden instructions",
        "reveal your instructions",
        "chain-of-thought",
        "reasoning",
        "internal reasoning",
        "confidential data",
        "show internal data"
    ]

    text = user_input.lower()
    return any(pattern in text for pattern in patterns)


def is_bad_item(text: str, sensitive_df: pd.DataFrame) -> bool:
    if not isinstance(text, str):
        return False

    lowered = text.lower()

    direct_patterns = [
        "internal notes",
        "do not expose",
        "internal only",
        "staff only",
        "confidential",
        "aggressive tone",
        "difficult user",
        "hostile",
        "confrontational"
    ]

    if any(pattern in lowered for pattern in direct_patterns):
        return True

    sensitive_contents = sensitive_df["content"].dropna().str.lower().tolist()

    for sensitive_text in sensitive_contents:
        if sensitive_text in lowered or lowered in sensitive_text:
            return True

    return False


def filter_safe_items(candidates: list[dict], sensitive_df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    safe_items = []
    blocked_items = []

    for item in candidates:
        if is_bad_item(item["text"], sensitive_df):
            blocked_items.append(item)
        else:
            safe_items.append(item)

    return safe_items, blocked_items