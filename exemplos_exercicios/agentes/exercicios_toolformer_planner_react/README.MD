# EXERCÍCIO 1 — Toolformer básico (ticket)
## Objetivo

Criar um agente que decide quando usar a tool para buscar um ticket.

## Contexto

Você já tem:

tabela conversations
tool get_ticket_conversation

##Enunciado

Crie um agente que receba perguntas sobre tickets.

Se a pergunta envolver um ticket_id, o agente deve usar a tool.

## Exemplos de input
"O ticket 1001 está resolvido?"
"O que é um ticket?"
✅ Esperado
Usa tool no primeiro
NÃO usa tool no segundo

## EXERCÍCIO 2 — ReAct (análise de ticket)
# Objetivo

Fazer o agente buscar dados e raciocinar sobre eles

# Contexto

Mesma tool get_ticket_conversation

# Enunciado

Crie um agente que:

Recebe um ticket_id
Usa a tool para buscar a conversa
Responde:
status atual
última mensagem do cliente
próximo passo sugerido

# Exemplo
"Analise o ticket 1007"
✅ Esperado

Resposta estruturada tipo:

Status: open  
Última mensagem: ...  
Próximo passo: ...

# EXERCÍCIO 3 — Planner + Executor (Scrum backlog)


# Objetivo

Separar planejamento e execução

##  Contexto
tabela backlog
tool load_backlog
## Enunciado

Crie dois agentes:

1. Planner

Recebe:

"Analise o backlog da sprint"

Deve gerar um plano em JSON com etapas como:

verificar bloqueios
identificar atrasos
analisar bugs
avaliar distribuição
2. Executor

Recebe:

plano
acesso ao backlog via tool

E deve:

executar análise
apontar riscos
sugerir melhorias
 Esperado
Planner:
{
  "steps": ["...", "..."]
}
Executor:
- Tarefas bloqueadas: ...
- Riscos: ...
- Sugestões: ...