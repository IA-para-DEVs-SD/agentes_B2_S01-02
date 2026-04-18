"""
Guardrail para validação de internal notes
Detecta PII e linguagem negativa/pejorativa
"""
import re


def detect_pii(text: str) -> dict:
    """
    Detecta informações pessoais identificáveis (PII) no texto
    
    Returns:
        dict com 'has_pii' (bool) e 'pii_types' (list)
    """
    pii_found = []
    
    # Email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.search(email_pattern, text):
        pii_found.append("email")
    
    # Telefone brasileiro (vários formatos)
    phone_patterns = [
        r'\b\d{2}\s?\d{4,5}-?\d{4}\b',  # 11 98888-8888 ou 1198888888
        r'\b\(\d{2}\)\s?\d{4,5}-?\d{4}\b',  # (11) 98888-8888
        r'\b\d{10,11}\b'  # 11988888888
    ]
    for pattern in phone_patterns:
        if re.search(pattern, text):
            pii_found.append("phone")
            break
    
    # CPF (formato XXX.XXX.XXX-XX ou XXXXXXXXXXX)
    cpf_patterns = [
        r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b',
        r'\b\d{11}\b'
    ]
    for pattern in cpf_patterns:
        if re.search(pattern, text):
            pii_found.append("cpf")
            break
    
    # Outros identificadores numéricos longos
    if re.search(r'\b\d{8,}\b', text) and "cpf" not in pii_found and "phone" not in pii_found:
        pii_found.append("numeric_id")
    
    return {
        "has_pii": len(pii_found) > 0,
        "pii_types": list(set(pii_found))
    }


def detect_negative_language(text: str) -> dict:
    """
    Detecta linguagem negativa ou pejorativa sobre usuários
    
    Returns:
        dict com 'has_negative' (bool) e 'negative_terms' (list)
    """
    negative_patterns = [
        "difficult user",
        "rude",
        "hostile",
        "aggressive",
        "manipulative",
        "annoying",
        "problematic",
        "troublesome",
        "complains frequently",
        "always complaining",
        "difficult to deal",
        "pain in",
        "nightmare",
        "terrible customer",
        "bad customer",
        "worst customer",
        "idiota",
        "chato",
        "problemático",
        "difícil",
        "agressivo",
        "hostil",
        "mal educado"
    ]
    
    text_lower = text.lower()
    found_terms = []
    
    for pattern in negative_patterns:
        if pattern in text_lower:
            found_terms.append(pattern)
    
    return {
        "has_negative": len(found_terms) > 0,
        "negative_terms": found_terms
    }


def sanitize_text(text: str, pii_info: dict, negative_info: dict) -> str:
    """
    Remove ou mascara PII e linguagem negativa do texto
    
    Returns:
        str com texto sanitizado
    """
    sanitized = text
    
    # Mascara emails
    if "email" in pii_info.get("pii_types", []):
        sanitized = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL_REDACTED]',
            sanitized
        )
    
    # Mascara telefones
    if "phone" in pii_info.get("pii_types", []):
        sanitized = re.sub(r'\b\d{2}\s?\d{4,5}-?\d{4}\b', '[PHONE_REDACTED]', sanitized)
        sanitized = re.sub(r'\b\(\d{2}\)\s?\d{4,5}-?\d{4}\b', '[PHONE_REDACTED]', sanitized)
        sanitized = re.sub(r'\b\d{10,11}\b', '[PHONE_REDACTED]', sanitized)
    
    # Mascara CPF
    if "cpf" in pii_info.get("pii_types", []):
        sanitized = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', '[CPF_REDACTED]', sanitized)
    
    # Remove termos negativos
    for term in negative_info.get("negative_terms", []):
        sanitized = re.sub(
            re.escape(term),
            '[REDACTED]',
            sanitized,
            flags=re.IGNORECASE
        )
    
    return sanitized


def validate_note(note_text: str, allow_sanitization: bool = True) -> dict:
    """
    Valida uma internal note e decide se deve ser salva, sanitizada ou bloqueada
    
    Args:
        note_text: Texto da nota a ser validada
        allow_sanitization: Se True, permite sanitização; se False, apenas bloqueia
    
    Returns:
        dict com:
            - status: 'saved', 'sanitized_and_saved', ou 'blocked'
            - original_text: texto original
            - sanitized_text: texto sanitizado (se aplicável)
            - issues: lista de problemas encontrados
            - details: detalhes dos problemas
    """
    pii_info = detect_pii(note_text)
    negative_info = detect_negative_language(note_text)
    
    issues = []
    details = {}
    
    if pii_info["has_pii"]:
        issues.append("PII detected")
        details["pii_types"] = pii_info["pii_types"]
    
    if negative_info["has_negative"]:
        issues.append("Negative language detected")
        details["negative_terms"] = negative_info["negative_terms"]
    
    # Decide o status
    if not issues:
        return {
            "status": "saved",
            "original_text": note_text,
            "sanitized_text": None,
            "issues": [],
            "details": {}
        }
    
    # Se tem problemas
    if allow_sanitization:
        sanitized = sanitize_text(note_text, pii_info, negative_info)
        return {
            "status": "sanitized_and_saved",
            "original_text": note_text,
            "sanitized_text": sanitized,
            "issues": issues,
            "details": details
        }
    else:
        return {
            "status": "blocked",
            "original_text": note_text,
            "sanitized_text": None,
            "issues": issues,
            "details": details
        }
