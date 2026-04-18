# Solução do Exercício 6 - Guardrails para Internal Notes

## ✅ Implementação Completa

Sistema de guardrails que valida internal notes antes de salvar no banco, detectando e tratando:
- **PII** (Personally Identifiable Information)
- **Linguagem negativa/pejorativa** sobre usuários

## 📁 Arquivos Criados

```
exe6/
├── guardrail_validator.py  # Lógica de validação e sanitização
├── db.py                    # Acesso ao banco de dados
├── process_note.py          # Script para processar notas individuais
├── test_cases.py            # Testes dos casos de uso
├── setup_db.py              # Setup da tabela no banco
└── SOLUCAO.md               # Esta documentação
```

## 🎯 Funcionalidades Implementadas

### 1. Detecção de PII
- ✅ Email (formato padrão)
- ✅ Telefone brasileiro (vários formatos)
- ✅ CPF (com ou sem formatação)
- ✅ Identificadores numéricos longos

### 2. Detecção de Linguagem Negativa
- ✅ Termos pejorativos em inglês e português
- ✅ Julgamentos sobre usuários
- ✅ Linguagem hostil ou agressiva

### 3. Estratégias de Tratamento
- **saved**: Nota segura, salva sem alterações
- **sanitized_and_saved**: Nota com problemas, mas sanitizada e salva
- **blocked**: Nota bloqueada (modo opcional)

## 🚀 Como Usar

### 1. Setup do Banco de Dados

```bash
python exemplos_exercicios/agentes/exe6/setup_db.py
```

Cria a tabela `internal_notes` se não existir.

### 2. Executar Testes

```bash
python exemplos_exercicios/agentes/exe6/test_cases.py
```

Executa 6 casos de teste cobrindo todos os cenários.

### 3. Processar Nota Individual

```bash
python exemplos_exercicios/agentes/exe6/process_note.py <ticket_id> "<note_text>"
```

**Exemplos:**

```bash
# Nota segura
python exemplos_exercicios/agentes/exe6/process_note.py 1 "Customer reported login failure"

# Nota com PII
python exemplos_exercicios/agentes/exe6/process_note.py 2 "Contact: joao@email.com"

# Nota com linguagem negativa
python exemplos_exercicios/agentes/exe6/process_note.py 3 "This is a difficult user"
```

## 📊 Resultados dos Testes

### CASO 1: Nota Segura
- **Input**: "Customer reported login failure after password reset."
- **Status**: ✅ saved
- **Ação**: Salva sem alterações

### CASO 2: Linguagem Negativa
- **Input**: "This is a difficult user and complains frequently."
- **Status**: 🔒 sanitized_and_saved
- **Output**: "This is a [REDACTED] and [REDACTED]."
- **Detectado**: difficult user, complains frequently

### CASO 3: PII (Email)
- **Input**: "Customer email is joao.silva@email.com and asked for an update."
- **Status**: 🔒 sanitized_and_saved
- **Output**: "Customer email is [EMAIL_REDACTED] and asked for an update."
- **Detectado**: email

### CASO 4: PII + Linguagem Negativa
- **Input**: "This rude customer called again. Phone: 41999998888"
- **Status**: 🔒 sanitized_and_saved
- **Output**: "This [REDACTED] customer called again. Phone: [PHONE_REDACTED]"
- **Detectado**: PII (phone, cpf), linguagem negativa (rude)

### CASO 5: CPF
- **Input**: "Customer CPF is 123.456.789-00 and needs verification."
- **Status**: 🔒 sanitized_and_saved
- **Output**: "Customer CPF is [CPF_REDACTED] and needs verification."
- **Detectado**: cpf

### CASO 6: Múltiplos PIIs
- **Input**: "Contact: joao@email.com or phone (11) 98888-7777. CPF: 12345678900"
- **Status**: 🔒 sanitized_and_saved
- **Output**: "Contact: [EMAIL_REDACTED] or phone [PHONE_REDACTED]. CPF: [PHONE_REDACTED]"
- **Detectado**: email, phone, cpf

## 📈 Taxa de Sucesso

```
✅ Passou: 6/6
❌ Falhou: 0/6
📈 Taxa de sucesso: 100.0%
```

## 🗄️ Estrutura da Tabela

```sql
CREATE TABLE internal_notes (
    id SERIAL PRIMARY KEY,
    ticket_id INT,
    note_text TEXT NOT NULL,
    note_status TEXT NOT NULL,
    blocked_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 Consultas Úteis

```sql
-- Ver todas as notas
SELECT * FROM internal_notes ORDER BY created_at DESC;

-- Ver apenas notas sanitizadas
SELECT * FROM internal_notes WHERE note_status = 'sanitized_and_saved';

-- Ver apenas notas bloqueadas
SELECT * FROM internal_notes WHERE note_status = 'blocked';

-- Contar por status
SELECT note_status, COUNT(*) 
FROM internal_notes 
GROUP BY note_status;
```

## 🛡️ Padrões Detectados

### PII
- Email: `usuario@dominio.com`
- Telefone: `11 98888-8888`, `(11) 98888-8888`, `11988888888`
- CPF: `123.456.789-00`, `12345678900`
- IDs numéricos: sequências de 8+ dígitos

### Linguagem Negativa
- difficult user, rude, hostile, aggressive
- manipulative, annoying, problematic
- complains frequently, pain in, nightmare
- difícil, chato, problemático, agressivo (PT-BR)

## 🎓 Conceitos Aplicados

1. **Regex para detecção de padrões** (PII)
2. **Pattern matching** para linguagem negativa
3. **Sanitização de dados** sensíveis
4. **Validação em camadas** (guardrails)
5. **Logging de decisões** (blocked_reason)
6. **Testes automatizados** com casos de uso reais

## 🔧 Personalização

Para adicionar novos padrões, edite `guardrail_validator.py`:

```python
# Adicionar novo tipo de PII
def detect_pii(text: str):
    # Adicione seu padrão aqui
    pass

# Adicionar novos termos negativos
negative_patterns = [
    "seu_novo_termo",
    # ...
]
```

## ✅ Conclusão

Sistema completo de guardrails implementado com sucesso, protegendo contra vazamento de PII e linguagem inadequada em internal notes!
