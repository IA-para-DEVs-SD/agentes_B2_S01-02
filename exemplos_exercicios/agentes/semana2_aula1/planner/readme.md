# 🧠 Exercício: Agente Scrum Master (Planner–Executor)

## 🎯 Objetivo

Construir um agente que:

1. **Lê o backlog** do banco (Postgres)
2. **Cria um plano de análise** (Planner)
3. **Executa esse plano** (Executor)
4. **Gera recomendações** como um Scrum Master

---

## 🧩 Cenário

Você tem uma tabela `backlog` no banco com tarefas da sprint.

O usuário pergunta:

> "Analise o backlog e me diga os principais riscos da sprint e o que devemos fazer."

---

## 📊 Estrutura do Banco

### Tabela: `backlog`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | ID da tarefa |
| `titulo` | TEXT | Título da tarefa |
| `descricao` | TEXT | Descrição detalhada |
| `prioridade` | TEXT | Alta, Média, Baixa |
| `status` | TEXT | To Do, In Progress, Done |
| `estimativa` | INTEGER | Pontos de história |
| `responsavel` | TEXT | Nome do responsável |

---

## 🔄 Fluxo do Agente

```
Usuário
   ↓
┌─────────────────────────────────┐
│  1. PLANNER                     │
│  • Analisa a pergunta           │
│  • Cria plano de ação           │
│  • Define tools necessárias     │
└─────────────────────────────────┘
   ↓
┌─────────────────────────────────┐
│  2. EXECUTOR                    │
│  • Executa cada step do plano   │
│  • Usa tools (SQL, análise)     │
│  • Coleta dados                 │
└─────────────────────────────────┘
   ↓
┌─────────────────────────────────┐
│  3. SYNTHESIZER                 │
│  • Consolida resultados         │
│  • Gera recomendações           │
│  • Formata resposta final       │
└─────────────────────────────────┘
   ↓
Resposta ao Usuário
```

---

## 🛠 Tools Disponíveis

### 1. `query_backlog`
Executa queries SQL no banco de dados.

**Exemplo:**
```python
query_backlog("SELECT * FROM backlog WHERE status = 'To Do'")
```

### 2. `analyze_risks`
Analisa riscos baseado em critérios (prioridade, estimativa, responsável).

**Exemplo:**
```python
analyze_risks(tasks_data)
```

### 3. `generate_recommendations`
Gera recomendações de ações para o Scrum Master.

**Exemplo:**
```python
generate_recommendations(risks_identified)
```

---

## 📝 Exemplo de Plano

```json
{
  "steps": [
    {
      "step": 1,
      "action": "query_backlog",
      "params": {
        "query": "SELECT * FROM backlog WHERE status != 'Done'"
      },
      "reason": "Buscar tarefas pendentes"
    },
    {
      "step": 2,
      "action": "analyze_risks",
      "params": {
        "criteria": ["prioridade", "estimativa", "responsavel"]
      },
      "reason": "Identificar riscos da sprint"
    },
    {
      "step": 3,
      "action": "generate_recommendations",
      "params": {
        "focus": "mitigação de riscos"
      },
      "reason": "Sugerir ações para o time"
    }
  ]
}
```

---

## 🚀 Como Rodar

### 1. Configurar o banco

```bash
# Subir o PostgreSQL
docker-compose up -d postgres

# Carregar dados de exemplo
python load_backlog_data.py
```

### 2. Executar o agente

```bash
python orchestration.py
```

### 3. Fazer uma pergunta

```python
from agent_planner import ScrumMasterAgent

agent = ScrumMasterAgent()
response = agent.run("Analise o backlog e identifique os principais riscos")
print(response)
```

---

## 📦 Estrutura de Arquivos

```
planner/
├── agent_planner.py      ← Agente Planner (cria o plano)
├── agent_exec.py         ← Agente Executor (executa o plano)
├── orchestration.py      ← Orquestrador (conecta Planner + Executor)
├── tools.py              ← Tools disponíveis
├── prompts.py            ← System prompts
└── readme.md             ← Este arquivo
```

---

## 🎓 Conceitos Aprendidos

- ✅ **Planner-Executor Pattern**: Separação entre planejamento e execução
- ✅ **Tool Calling**: Uso de ferramentas especializadas
- ✅ **SQL Integration**: Integração com banco de dados
- ✅ **Multi-step Reasoning**: Raciocínio em múltiplas etapas
- ✅ **Orchestration**: Coordenação entre agentes

---

## 🔍 Exemplo de Saída

```
🎯 ANÁLISE DO BACKLOG

📊 Resumo:
- Total de tarefas: 15
- Pendentes: 8
- Em progresso: 4
- Concluídas: 3

⚠️ Riscos Identificados:

1. ALTO RISCO - Tarefa #12: "Implementar autenticação"
   • Prioridade: Alta
   • Estimativa: 13 pontos
   • Responsável: João (sobrecarregado)
   • Motivo: Alta complexidade + responsável com muitas tarefas

2. MÉDIO RISCO - Tarefa #7: "Integração com API externa"
   • Prioridade: Alta
   • Estimativa: 8 pontos
   • Responsável: Maria
   • Motivo: Dependência externa

💡 Recomendações:

1. Redistribuir tarefas de João para outros membros
2. Priorizar tarefa #12 no início da sprint
3. Iniciar integração com API externa o quanto antes
4. Considerar pair programming para tarefas de alta complexidade
```

---

## 🧪 Exercícios Extras

1. **Adicionar nova tool**: Crie uma tool que busca informações externas sobre tecnologias
2. **Melhorar o planner**: Faça o planner considerar dependências entre tarefas
3. **Adicionar métricas**: Calcule velocity e burndown da sprint
4. **Integrar com Slack**: Envie notificações automáticas para o time

---

## 📚 Referências

- [ReAct Pattern](https://arxiv.org/abs/2210.03629)
- [Tool Calling Best Practices](https://platform.openai.com/docs/guides/function-calling)
- [Scrum Guide](https://scrumguides.org/)
