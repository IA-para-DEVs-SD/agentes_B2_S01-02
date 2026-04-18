"""
Script para processar e salvar internal notes com guardrails
"""
import sys
from guardrail_validator import validate_note
from db import save_internal_note


def process_and_save_note(ticket_id: int, note_text: str, allow_sanitization: bool = True):
    """
    Processa uma nota aplicando guardrails e salva no banco
    
    Args:
        ticket_id: ID do ticket
        note_text: Texto da nota
        allow_sanitization: Se True, permite sanitização; se False, apenas bloqueia
    
    Returns:
        dict com resultado do processamento
    """
    print("\n" + "="*60)
    print(f"📝 Processando nota para ticket {ticket_id}")
    print("="*60)
    print(f"\nTexto original:\n{note_text}\n")
    
    # Valida a nota
    validation_result = validate_note(note_text, allow_sanitization)
    
    status = validation_result["status"]
    issues = validation_result["issues"]
    details = validation_result["details"]
    
    print("🔍 Análise de Guardrails:")
    
    if not issues:
        print("   ✅ Nenhum problema detectado")
    else:
        print(f"   ⚠️  Problemas encontrados: {len(issues)}")
        for issue in issues:
            print(f"      - {issue}")
        
        if "pii_types" in details:
            print(f"      PII detectado: {', '.join(details['pii_types'])}")
        
        if "negative_terms" in details:
            print(f"      Termos negativos: {', '.join(details['negative_terms'])}")
    
    print(f"\n📊 Status: {status.upper()}")
    
    # Prepara dados para salvar
    text_to_save = note_text
    blocked_reason = None
    
    if status == "sanitized_and_saved":
        text_to_save = validation_result["sanitized_text"]
        print(f"\n🔒 Texto sanitizado:\n{text_to_save}")
        blocked_reason = f"Sanitized: {', '.join(issues)}"
    
    elif status == "blocked":
        blocked_reason = f"Blocked: {', '.join(issues)}"
        print(f"\n🚫 Nota BLOQUEADA")
        print(f"   Motivo: {blocked_reason}")
    
    # Salva no banco
    try:
        note_id = save_internal_note(ticket_id, text_to_save, status, blocked_reason)
        print(f"\n✅ Nota salva no banco com ID: {note_id}")
    except Exception as e:
        print(f"\n❌ Erro ao salvar no banco: {e}")
        return None
    
    print("="*60 + "\n")
    
    return {
        "note_id": note_id,
        "status": status,
        "issues": issues,
        "original_text": note_text,
        "saved_text": text_to_save
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\n❌ Uso: python process_note.py <ticket_id> <note_text>")
        print("Exemplo: python process_note.py 1 \"Customer reported login failure\"")
        sys.exit(1)
    
    ticket_id = int(sys.argv[1])
    note_text = sys.argv[2]
    
    process_and_save_note(ticket_id, note_text)
