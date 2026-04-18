# Agente 03 - Auditor de Qualidade

## O que faz
Recebe os outputs dos Agentes 01 e 02, valida consistência e pontua a qualidade dos artefatos.

## Input
- Backlog técnico (JSON do Agente 01)
- Documento de requisitos (JSON do Agente 02)

## Output (JSON)
- `audit_summary` — resumo da auditoria
- `consistency_check` — status e problemas encontrados
- `gaps` — lacunas com severidade
- `quality_score` — score total e breakdown por critério
- `suggestions` — sugestões de melhoria
- `missing_requirements` — requisitos faltantes
- `final_recommendation` — aprovado / refinamento / retrabalho

## Tools utilizadas
- `score_quality` — avalia completude, clareza, testabilidade e consistência

## Como rodar

```bash
# Standalone
docker compose up audit-agent --build

# Pipeline completo (todos em sequência)
docker compose up --build
```

## Dependências
- `openai`
- `python-dotenv`
