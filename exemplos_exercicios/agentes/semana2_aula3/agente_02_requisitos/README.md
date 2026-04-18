# Agente 02 - Analista de Requisitos

## O que faz
Recebe o backlog do Agente 01 (Scrum Master) e produz um documento estruturado de requisitos.

## Input
- Backlog técnico (JSON do Agente 01)

## Output (JSON)
- `functional_requirements` — requisitos funcionais com IDs e tarefas relacionadas
- `non_functional_requirements` — requisitos não-funcionais categorizados
- `dependency_map` — mapa de dependências entre componentes
- `risks` — riscos com severidade e mitigação
- `notes` — observações gerais

## Tools utilizadas
- `find_edges` — analisa tarefas e retorna dependências entre componentes do sistema

## Como rodar

```bash
# Standalone (usa dados de exemplo)
docker compose up requirements-agent --build

# Ou via pipeline (quando integrado ao orchestrator)
docker compose up --build
```

## Dependências
- `openai`
- `python-dotenv`
