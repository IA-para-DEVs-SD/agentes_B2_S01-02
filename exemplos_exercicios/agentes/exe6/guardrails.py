import re


# --- Detecção de PII ---

PII_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),
    (r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "cpf"),
    (r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b", "cnpj"),
    (r"\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b", "telefone"),
]


def detect_pii(text: str) -> list[dict]:
    """Detecta PII no texto e retorna lista de ocorrências."""
    findings = []
    for pattern, pii_type in PII_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            findings.append({"type": pii_type, "value": match})
    return findings


def sanitize_pii(text: str) -> str:
    """Remove PII do texto substituindo por placeholders."""
    result = text
    for pattern, pii_type in PII_PATTERNS:
        result = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", result)
    return result


# --- Detecção de linguagem negativa ---

NEGATIVE_PATTERNS = [
    "difficult user",
    "difficult customer",
    "rude",
    "hostile",
    "aggressive",
    "manipulative",
    "confrontational",
    "annoying",
    "stupid",
    "idiot",
    "incompetent",
    "ignorant",
    "complains frequently",
    "always complaining",
    "problema recorrente do usuário",
    "usuário difícil",
    "usuário agressivo",
    "usuário rude",
    "grosso",
    "mal educado",
]


def detect_negative_language(text: str) -> list[str]:
    """Detecta linguagem negativa/pejorativa sobre o usuário."""
    text_lower = text.lower()
    found = [p for p in NEGATIVE_PATTERNS if p in text_lower]
    return found


def sanitize_negative_language(text: str) -> str:
    """Remove trechos com linguagem negativa."""
    result = text
    for pattern in NEGATIVE_PATTERNS:
        result = re.sub(re.escape(pattern), "[REDACTED]", result, flags=re.IGNORECASE)
    return result


# --- Validação completa ---

def validate_note(note_text: str) -> dict:
    """
    Valida uma internal note e retorna o resultado da decisão.

    Retorna:
        {
            "original_text": str,
            "status": "saved" | "sanitized_and_saved" | "blocked",
            "pii_found": list,
            "negative_language_found": list,
            "sanitized_text": str | None,
            "blocked_reason": str | None,
        }
    """
    pii_found = detect_pii(note_text)
    negative_found = detect_negative_language(note_text)

    has_pii = len(pii_found) > 0
    has_negative = len(negative_found) > 0

    # Caso sem problemas
    if not has_pii and not has_negative:
        return {
            "original_text": note_text,
            "status": "saved",
            "pii_found": [],
            "negative_language_found": [],
            "sanitized_text": None,
            "blocked_reason": None,
        }

    # Caso com ambos os problemas -> bloquear
    if has_pii and has_negative:
        return {
            "original_text": note_text,
            "status": "blocked",
            "pii_found": pii_found,
            "negative_language_found": negative_found,
            "sanitized_text": None,
            "blocked_reason": "PII e linguagem negativa detectados",
        }

    # Caso com apenas PII -> sanitizar e salvar
    if has_pii:
        sanitized = sanitize_pii(note_text)
        return {
            "original_text": note_text,
            "status": "sanitized_and_saved",
            "pii_found": pii_found,
            "negative_language_found": [],
            "sanitized_text": sanitized,
            "blocked_reason": None,
        }

    # Caso com apenas linguagem negativa -> bloquear
    return {
        "original_text": note_text,
        "status": "blocked",
        "pii_found": [],
        "negative_language_found": negative_found,
        "sanitized_text": None,
        "blocked_reason": "Linguagem negativa/pejorativa detectada",
    }
