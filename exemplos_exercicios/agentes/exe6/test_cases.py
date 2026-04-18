"""
Testes dos casos de uso do exercício 6
"""
from guardrail_validator import validate_note
from db import save_internal_note


def run_test_case(case_number: int, description: str, note_text: str, expected_status: str):
    """
    Executa um caso de teste
    """
    print("\n" + "="*60)
    print(f"CASO {case_number}: {description}")
    print("="*60)
    print(f"\n📝 Nota: \"{note_text}\"")
    
    # Valida a nota
    result = validate_note(note_text, allow_sanitization=True)
    
    status = result["status"]
    issues = result["issues"]
    
    print(f"\n🔍 Problemas detectados: {len(issues)}")
    if issues:
        for issue in issues:
            print(f"   - {issue}")
        
        if result["details"].get("pii_types"):
            print(f"   PII: {', '.join(result['details']['pii_types'])}")
        
        if result["details"].get("negative_terms"):
            print(f"   Termos negativos: {', '.join(result['details']['negative_terms'])}")
    
    print(f"\n📊 Status: {status}")
    
    if result["sanitized_text"]:
        print(f"🔒 Texto sanitizado: \"{result['sanitized_text']}\"")
    
    # Verifica se passou
    status_match = status == expected_status or (
        expected_status in ["sanitized_and_saved", "blocked"] and 
        status in ["sanitized_and_saved", "blocked"]
    )
    
    if status_match:
        print(f"\n✅ PASSOU - Status esperado: {expected_status}")
    else:
        print(f"\n❌ FALHOU - Esperado: {expected_status}, Obtido: {status}")
    
    # Salva no banco
    try:
        text_to_save = result["sanitized_text"] if result["sanitized_text"] else note_text
        blocked_reason = f"{', '.join(issues)}" if issues else None
        note_id = save_internal_note(case_number, text_to_save, status, blocked_reason)
        print(f"💾 Salvo no banco com ID: {note_id}")
    except Exception as e:
        print(f"⚠️  Erro ao salvar: {e}")
    
    return status_match


def main():
    print("\n" + "="*60)
    print("🧪 TESTES DE GUARDRAILS - Exercício 6")
    print("="*60)
    
    test_results = []
    
    # Caso 1: Nota segura
    test_results.append(run_test_case(
        1,
        "Nota segura (sem problemas)",
        "Customer reported login failure after password reset.",
        "saved"
    ))
    
    # Caso 2: Nota com julgamento negativo
    test_results.append(run_test_case(
        2,
        "Nota com julgamento negativo",
        "This is a difficult user and complains frequently.",
        "sanitized_and_saved"  # ou "blocked"
    ))
    
    # Caso 3: Nota com PII (email)
    test_results.append(run_test_case(
        3,
        "Nota com PII (email)",
        "Customer email is joao.silva@email.com and asked for an update.",
        "sanitized_and_saved"  # ou "blocked"
    ))
    
    # Caso 4: Nota com dois problemas (PII + linguagem negativa)
    test_results.append(run_test_case(
        4,
        "Nota com PII e linguagem negativa",
        "This rude customer called again. Phone: 41999998888",
        "sanitized_and_saved"  # ou "blocked"
    ))
    
    # Casos adicionais
    test_results.append(run_test_case(
        5,
        "Nota com CPF",
        "Customer CPF is 123.456.789-00 and needs verification.",
        "sanitized_and_saved"
    ))
    
    test_results.append(run_test_case(
        6,
        "Nota com múltiplos PIIs",
        "Contact: joao@email.com or phone (11) 98888-7777. CPF: 12345678900",
        "sanitized_and_saved"
    ))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    passed = sum(test_results)
    total = len(test_results)
    print(f"\n✅ Passou: {passed}/{total}")
    print(f"❌ Falhou: {total - passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
