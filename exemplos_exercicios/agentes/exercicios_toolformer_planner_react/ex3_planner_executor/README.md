# Exercício 3 - Planner + Executor

## Objetivo

Implementar o padrão de agentes Planner + Executor para análise de backlog Scrum.

## O que é Planner + Executor?

É um padrão de arquitetura de agentes que separa:

### Planner (Planejador)
- **Responsabilidade**: Criar planos de ação estruturados
- **Não executa**: Apenas define O QUE fazer
- **Output**: Plano em JSON com etapas claras

### Executor (Executor)
- **Responsabilidade**: Executar o plano criado
- **Tem acesso a tools**: Busca dados e executa análises
- **Output**: Relatório com resultados, riscos e sugestões

## Vantagens do Padrão

1. **Separação de responsabilidades**: Planejamento vs Execução
2. **Reutilização**: Mesmo plano pode ser executado múltiplas vezes
3. **Flexibilidade**: Planos podem ser ajustados antes da execução
4. **Auditoria**: Plano registrado permite rastreamento

## Arquitetura

```
User Request
     ↓
  PLANNER → Cria plano JSON
     ↓
  EXECUTOR → Executa plano usando tools
     ↓
  Relatório Final
```

## Arquivos

- `tools.py`: Tool load_backlog para acessar dados
- `planner_agent.py`: Agente que cria planos
- `executor_agent.py`: Agente que executa planos
- `orchestrator.py`: Coordena Planner + Executor
- `README.md`: Esta documentação

## Como Executar

### Opção 1: Orchestrator (Recomendado)
```bash
python orchestrator.py
```

### Opção 2: Separado
```bash
# 1. Criar plano
python planner_agent.py

# 2. Executar plano
python executor_agent.py
```

### Opção 3: Testar tool
```bash
python tools.py
```

## Exemplo de Plano Gerado

```json
{
  "objetivo": "Análise completa do backlog da sprint",
  "steps": [
    "Carregar dados do backlog usando load_backlog",
    "Verificar tarefas bloqueadas e seus impactos",
    "Identificar atrasos baseado em dias_em_aberto",
    "Analisar distribuição de bugs relacionados",
    "Avaliar distribuição de trabalho entre responsáveis",
    "Identificar riscos para a sprint",
    "Sugerir melhorias e ações corretivas"
  ]
}
```

## Exemplo de Relatório Gerado

```
TAREFAS BLOQUEADAS:
- Refatorar API (Diego) - 10 dias em aberto, 4 bugs relacionados

ATRASOS:
- Melhorar dashboard (Carla) - 15 dias em aberto
- Corrigir pagamento (Bruno) - 12 dias em aberto

BUGS:
- Total: 16 bugs relacionados
- Maior concentração: Refatorar API (4 bugs)

DISTRIBUIÇÃO DE TRABALHO:
- Ana: 2 tarefas, 7 story points
- Bruno: 2 tarefas, 16 story points
- Carla: 2 tarefas, 8 story points
- Diego: 1 tarefa, 13 story points

RISCOS:
- Tarefa bloqueada de alta prioridade pode atrasar sprint
- Concentração de bugs em API crítica

SUGESTÕES:
- Desbloquear "Refatorar API" com urgência
- Redistribuir carga de Bruno (16 pontos)
- Priorizar correção de bugs na API
```

## Diferenças entre os Exercícios

### Ex1 - Toolformer
- Decide SE usar tool
- Foco: seleção de tools

### Ex2 - ReAct
- Raciocínio + Ação + Observação
- Foco: análise contextual

### Ex3 - Planner + Executor
- Separação: Planejamento vs Execução
- Foco: arquitetura de agentes
- Escalável para tarefas complexas
