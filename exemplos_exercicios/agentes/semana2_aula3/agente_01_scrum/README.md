# Agente 01 - Scrum Master

## O que faz
Recebe uma user story e a transforma em um backlog técnico estruturado e priorizado.

## Input
- História de usuário (texto livre)

## Output (JSON)
- `user_story_rewritten` — história reescrita no formato padrão
- `acceptance_criteria` — critérios de aceitação
- `tasks` — lista de tarefas com id, título, descrição, prioridade, esforço e dependências
- `dependencies_map` — mapa de dependências entre tarefas
- `open_questions` — dúvidas para refinamento
- `risks` — riscos identificados
- `notes` — observações gerais

## Tools utilizadas
- `break_tasks` — quebra a user story em tarefas técnicas com prioridade e esforço

## Como rodar

```bash
# Da raiz do projeto
python exemplos_exercicios/agentes/semana2_aula3/agente_01_scrum/agent.py

# Ou de dentro da pasta
cd exemplos_exercicios/agentes/semana2_aula3/agente_01_scrum
python agent.py
```

## Dependências
- `openai`
- `python-dotenv`
