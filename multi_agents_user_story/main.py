"""
Multi-Agent User Story Analyzer
Ponto de entrada principal.

Usa o Orchestrator para coordenar os agentes em sequência:
1. Scrum Master → backlog priorizado
2. Requisitos Ocultos → edge cases, riscos, dependências
3. (Futuro) Auditoria → relatório final com score
"""
from orchestrator import Orchestrator, main

if __name__ == "__main__":
    main()
