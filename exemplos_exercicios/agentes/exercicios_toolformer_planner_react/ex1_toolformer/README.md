# Exercício 1 - Toolformer Básico

## 📌 Objetivo

Criar um agente que **decide inteligentemente quando usar uma tool** para buscar informações de tickets.

## 🎯 Conceito: Toolformer

**Toolformer** é um padrão onde o agente aprende a decidir quando chamar ferramentas externas baseado no contexto da pergunta.

### Comportamento Esperado

- ✅ **USA tool** quando a pergunta menciona um ticket_id específico
- ❌ **NÃO USA tool** quando a pergunta é genérica ou não requer dados específicos

## 📁 Arquivos

```
ex1_toolformer/
├── tools.py              # Tool get_ticket_conversation
├── toolformer_agent.py   # Agente Toolformer
└── README.md            # Esta documentação
```

## 🔧 Tool Disponível

### `get_ticket_conversation(ticket_id: int)`

Busca informações completas de um ticket:
- Status atual
- Todas as mensagens da conversa
- Timestamps
- Contagem de mensagens

**Retorno:**
```python
{
    "ticket_id": 1001,
    "found": True,
    "status": "open",
    "messages": [...],
    "conversation_text": "...",
    "message_count": 5
}
```

## 🚀 Como Executar

### Pré-requisitos

1. Banco de dados PostgreSQL rodando
2. Chave GEMINI_API_KEY configurada no .env
3. Tabela `conversations` populada

### Executar o Agente

```bash
python exemplos_exercicios/agentes/exercicios_toolformer_planner_react/ex1_toolformer/toolformer_agent.py
```

## 📊 Casos de Teste

### Teste 1: Pergunta com ticket_id ✅

**Input:** "O ticket 1001 está resolvido?"

**Comportamento esperado:**
- 🔧 Usa a tool `get_ticket_conversation(1001)`
- 📊 Busca dados do ticket no banco
- 💬 Responde baseado nos dados reais

**Exemplo de resposta:**
```
O ticket 1001 ainda está em aberto (status: open). 
A última mensagem foi do cliente solicitando atualização.
```

### Teste 2: Pergunta genérica ❌

**Input:** "O que é um ticket?"

**Comportamento esperado:**
- ℹ️ NÃO usa a tool
- 💬 Responde com conhecimento geral

**Exemplo de resposta:**
```
Um ticket é um registro de solicitação ou problema 
reportado por um cliente ao suporte técnico.
```

### Teste 3: Pergunta sobre status ✅

**Input:** "Qual o status do ticket 1007?"

**Comportamento esperado:**
- 🔧 Usa a tool `get_ticket_conversation(1007)`
- 📊 Busca dados do ticket
- 💬 Informa o status atual

## 🎓 Conceitos Aplicados

### 1. Decisão Inteligente

O agente analisa a pergunta e decide se precisa de dados externos:

```python
# Pergunta com ticket_id → USA tool
"O ticket 1001 está resolvido?"

# Pergunta genérica → NÃO USA tool
"O que é um ticket?"
```

### 2. Tool Calling

Quando necessário, o agente chama a tool com os parâmetros corretos:

```python
get_ticket_conversation(ticket_id=1001)
```

### 3. Raciocínio Contextual

O agente entende o contexto e responde apropriadamente:
- Com dados reais quando disponíveis
- Com conhecimento geral quando apropriado

## 📈 Fluxo de Execução

```
1. Usuário faz pergunta
   ↓
2. Agente analisa a pergunta
   ↓
3. Decisão: Precisa de tool?
   ├─ SIM → Chama get_ticket_conversation()
   │         ↓
   │         Recebe dados do banco
   │         ↓
   │         Responde com dados reais
   │
   └─ NÃO → Responde com conhecimento geral
```

## 🔍 Exemplo de Saída

```
============================================================
🤖 AGENTE TOOLFORMER - Exercício 1
============================================================

============================================================
TESTE 1: Pergunta com ticket_id específico
============================================================

============================================================
❓ Pergunta: O ticket 1001 está resolvido?
============================================================

🔧 Usando tool: get_ticket_conversation
   Argumentos: {'ticket_id': 1001}
   ✅ Ticket encontrado - Status: open

✅ Tool foi utilizada

📝 Resposta:
Não, o ticket 1001 ainda não está resolvido. 
O status atual é "open" (aberto).

============================================================
TESTE 2: Pergunta genérica sobre tickets
============================================================

============================================================
❓ Pergunta: O que é um ticket?
============================================================

ℹ️  Respondeu sem usar tool

📝 Resposta:
Um ticket é um registro ou solicitação de suporte técnico 
criado quando um cliente reporta um problema ou faz uma pergunta.
```

## 🎯 Critérios de Sucesso

- ✅ Usa tool quando há ticket_id específico
- ✅ NÃO usa tool para perguntas genéricas
- ✅ Responde corretamente em ambos os casos
- ✅ Extrai ticket_id corretamente da pergunta
- ✅ Trata casos de ticket não encontrado

## 🔧 Personalização

### Adicionar Mais Tools

Edite `tools.py`:

```python
def nova_tool(parametro: str) -> dict:
    # Implementação
    pass

TOOL_MAP = {
    "get_ticket_conversation": get_ticket_conversation,
    "nova_tool": nova_tool
}
```

### Ajustar Comportamento

Edite o prompt em `toolformer_agent.py`:

```python
text=(
    "Você é um assistente de suporte técnico.\n\n"
    "Suas instruções personalizadas aqui...\n\n"
    f"Pergunta do usuário: {user_question}"
)
```

## 🆚 Diferença para Outros Padrões

| Padrão | Característica |
|--------|----------------|
| **Toolformer** | Decide QUANDO usar tools |
| ReAct | Raciocina SOBRE dados obtidos |
| Planner | PLANEJA sequência de ações |

## ✅ Conclusão

O agente Toolformer implementado com sucesso demonstra:
- Decisão inteligente sobre uso de ferramentas
- Integração com banco de dados via tools
- Respostas contextualizadas
- Tratamento de casos com e sem tools

Pronto para o próximo exercício (ReAct)! 🚀
