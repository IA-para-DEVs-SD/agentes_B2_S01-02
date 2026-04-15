Arquitetura proposta
Agente 1 — Scrum Master

Responsável por interpretar a User Story e transformá-la em itens mais acionáveis.

Funções
analisar a User Story
quebrar em tarefas menores
priorizar backlog inicial
consultar exemplos ou referências externas
salvar resultado no Qdrant
Tools sugeridas
search_exa()
break_tasks()
prioritize()
Saída esperada
backlog inicial
lista de tarefas
prioridades
resumo para o próximo agente
Agente 2 — Requisitos Ocultos

Responsável por identificar o que não foi explicitado, mas é necessário para boa execução.

Funções
buscar lacunas na User Story
identificar dependências
levantar edge cases
consultar memória vetorial para recuperar contexto anterior
salvar nova análise no Qdrant
Tools sugeridas
search_exa()
find_edge_cases()
search_qdrant()
Saída esperada
requisitos implícitos
riscos
dependências
casos de borda
resumo para o próximo agente
Agente 3 — Auditoria

Responsável por avaliar a qualidade final da User Story e da análise acumulada.

Funções
revisar backlog, riscos e requisitos ocultos
aplicar critérios de qualidade
atribuir score
gerar relatório final consolidado
Tools sugeridas
audit_reqs()
score_quality()
search_qdrant()
Saída esperada
score de qualidade
inconsistências encontradas
sugestões de melhoria
relatório final
Memória compartilhada

O sistema deve usar dois tipos de memória:

1. Short-term memory

Usar messages[] para passar o resumo do output anterior para o próximo agente.

Essa memória representa o contexto imediato da execução atual.

Exemplo

O Agente 1 envia ao Agente 2:

resumo da User Story
backlog gerado
principais prioridades
2. Long-term memory

Salvar os outputs dos agentes no Qdrant usando embeddings.

Essa memória representa contexto persistente e buscável semanticamente.

Exemplo

O Agente 2 pode buscar no Qdrant:

User Stories parecidas
riscos semelhantes encontrados antes
padrões de edge cases já registrados
Regra de uso conjunto
messages[] = contexto rápido e imediato
Qdrant = memória persistente e recuperação semântica
os dois devem ser usados juntos
Fluxo do sistema
Entrada

Uma User Story com critérios de aceitação.

Etapas
O orquestrador recebe a User Story
Envia para o Agente 1
O Agente 1 processa, usa tools, salva no Qdrant e gera resumo
O orquestrador passa esse resumo ao Agente 2
O Agente 2 complementa a análise, consulta Qdrant, salva sua saída e gera resumo
O orquestrador passa esse resumo ao Agente 3
O Agente 3 audita tudo e gera o relatório final
Saída

Um relatório consolidado contendo:

backlog priorizado
requisitos ocultos
riscos e dependências
edge cases
score de qualidade
sugestões de melhoria
Estrutura mínima do relatório final

O relatório final deve conter, no mínimo:

1. Resumo da User Story
descrição curta
objetivo do usuário
2. Backlog sugerido
lista de tarefas
prioridade
3. Requisitos ocultos
itens não explícitos
dependências técnicas ou funcionais
4. Edge cases
cenários extremos
falhas possíveis
exceções
5. Riscos identificados
riscos de implementação
riscos de negócio
riscos de experiência do usuário
6. Auditoria de qualidade
clareza
testabilidade
completude
consistência
7. Score final

Exemplo:

clareza: 8/10
completude: 6/10
testabilidade: 7/10
score geral: 7/10
8. Sugestões de melhoria
reescrita da User Story
critérios de aceitação ausentes
detalhes que deveriam ser adicionados
Requisitos técnicos do exercício

Os alunos devem implementar:

um orquestrador
três agentes especializados
pelo menos uma tool real ou simulada por agente
persistência de memória no Qdrant
passagem de contexto entre agentes usando messages[]
Sugestão de organização do projeto
multi_agents_user_story/
│
├── orchestrator.py
├── agents/
│   ├── scrum_master.py
│   ├── hidden_requirements.py
│   └── auditor.py
│
├── tools/
│   ├── exa_search.py
│   ├── task_breaker.py
│   ├── prioritizer.py
│   ├── edge_cases.py
│   ├── auditor_tools.py
│   └── qdrant_memory.py
│
├── models/
│   └── schemas.py
│
├── data/
│   └── sample_user_stories.json
│
└── main.py
Exemplo de entrada
Como usuário, quero redefinir minha senha para recuperar o acesso à minha conta.

Critérios de aceitação:
- O usuário deve poder solicitar redefinição por e-mail
- O link deve expirar após um período
- O sistema deve confirmar quando a senha for alterada
Exemplo de saída esperada
{
  "user_story_summary": "Recuperação de acesso via redefinição de senha",
  "backlog": [
    {"task": "Criar fluxo de solicitação por e-mail", "priority": "Alta"},
    {"task": "Gerar token temporário", "priority": "Alta"},
    {"task": "Implementar expiração do link", "priority": "Média"},
    {"task": "Enviar confirmação de alteração", "priority": "Média"}
  ],
  "hidden_requirements": [
    "Validação de e-mail cadastrado",
    "Proteção contra reutilização de token",
    "Registro de auditoria da alteração"
  ],
  "edge_cases": [
    "Link expirado",
    "Token inválido",
    "Usuário solicita múltiplos links",
    "Tentativa de redefinição para conta bloqueada"
  ],
  "risks": [
    "Falhas de segurança no fluxo de token",
    "Experiência ruim se o e-mail atrasar",
    "Falta de rastreabilidade em alterações de senha"
  ],
  "quality_score": {
    "clarity": 8,
    "completeness": 7,
    "testability": 8,
    "overall": 7.7
  },
  "suggestions": [
    "Especificar prazo exato de expiração do link",
    "Adicionar critério para tokens já utilizados",
    "Incluir requisito de logging e auditoria"
  ]
}