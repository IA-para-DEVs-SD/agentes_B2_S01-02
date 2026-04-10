# Plano de Implementação: Ghost User Detection

## Visão Geral

Implementar o script `ghost_detector.py` em Python usando pandas, seguindo o pipeline: carregar CSV → ordenar → identificar último speaker e status final → classificar tickets → sugerir ações → atribuir prioridades → gerar JSONs → imprimir reflexões. Funções puras para lógica de negócio facilitam testes.

## Tarefas

- [x] 1. Criar estrutura base e funções de carregamento/validação
  - [x] 1.1 Criar o arquivo `exemplos_exercicios/exercicio_2/ghost_detector.py` com imports, constantes e a função `load_and_validate_csv`
    - Importar `pandas`, `json`, `sys`, `os`
    - Definir `REQUIRED_COLUMNS`, `VALID_SPEAKERS`, `VALID_STATUSES`
    - Implementar `load_and_validate_csv(filepath: str) -> pd.DataFrame` que carrega o CSV, valida colunas obrigatórias, converte `timestamp` para datetime e encerra com mensagem descritiva se o arquivo não existir ou faltar colunas
    - _Requisitos: 1.1, 1.2, 1.3, 1.4_

  - [x] 1.2 Implementar `sort_data` e funções de extração (`get_last_speaker`, `get_final_status`)
    - `sort_data(df) -> pd.DataFrame`: ordena por `conversation_id` e `timestamp` crescentes, preservando todas as linhas
    - `get_last_speaker(df) -> pd.DataFrame`: para cada `conversation_id`, retorna `[ticket_id, conversation_id, speaker]` da última mensagem
    - `get_final_status(df) -> pd.DataFrame`: para cada `ticket_id`, retorna `[ticket_id, ticket_status]` da última mensagem
    - _Requisitos: 2.1, 2.2, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_

- [x] 2. Implementar lógica de classificação e ações
  - [x] 2.1 Implementar `classify_ticket` e `classify_all_tickets`
    - `classify_ticket(last_speaker: str, final_status: str) -> str` aplica as regras: atendente+pending→precisa_follow_up, atendente+closed→encerrado, client+solved→resolvido, atendente+open→risco, client+≠solved→ativo
    - `classify_all_tickets(last_speakers: pd.DataFrame, final_statuses: pd.DataFrame) -> list[dict]` combina dados e retorna lista de `{"ticket_id": int, "status": str}`
    - _Requisitos: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 2.2 Escrever testes de propriedade para `classify_ticket`
    - **Propriedade 1: Cobertura total das regras de classificação** — para qualquer combinação válida de `(speaker, status)`, `classify_ticket` sempre retorna um valor em `{"precisa_follow_up", "encerrado", "resolvido", "risco", "ativo"}`
    - **Valida: Requisitos 5.1, 5.2, 5.3, 5.4, 5.5**

  - [x] 2.3 Implementar `suggest_action`
    - `suggest_action(classification: str) -> str` mapeia: precisa_follow_up→send_follow_up, risco→monitor, encerrado/resolvido/ativo→no_action
    - _Requisitos: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ]* 2.4 Escrever testes de propriedade para `suggest_action`
    - **Propriedade 2: Mapeamento determinístico de ação** — para qualquer classificação válida, `suggest_action` retorna um valor em `{"send_follow_up", "monitor", "no_action"}`
    - **Valida: Requisitos 7.1, 7.2, 7.3, 7.4, 7.5**

  - [x] 2.5 Implementar `assign_priority`
    - `assign_priority(classification: str, final_status: str) -> str` atribui: risco→high, pending→medium, closed/solved→low, demais→medium
    - _Requisitos: 9.1, 9.2, 9.3_

  - [ ]* 2.6 Escrever testes de propriedade para `assign_priority`
    - **Propriedade 3: Prioridade sempre válida** — para qualquer combinação válida de `(classification, final_status)`, `assign_priority` retorna um valor em `{"high", "medium", "low"}`
    - **Valida: Requisitos 9.1, 9.2, 9.3**

- [x] 3. Checkpoint — Verificar testes e lógica de negócio
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 4. Implementar geração de saídas JSON e reflexões
  - [x] 4.1 Implementar `generate_json` e geração dos arquivos de saída
    - `generate_json(data: list[dict], filepath: str) -> None` serializa com `indent=2` e encoding UTF-8
    - Gerar `conversation_status.json` com `[{"ticket_id": int, "status": str}]`, um registro por ticket
    - Gerar `ticket_actions.json` com `[{"ticket_id": int, "action": str, "priority": str}]`, um registro por ticket
    - _Requisitos: 6.1, 6.2, 6.3, 6.4, 8.1, 8.2, 8.3, 8.4, 9.4_

  - [ ]* 4.2 Escrever testes unitários para `generate_json`
    - Verificar que o arquivo é criado com JSON válido, indentação correta e encoding UTF-8
    - Verificar que cada ticket aparece exatamente uma vez em cada arquivo de saída
    - _Requisitos: 6.2, 6.3, 6.4, 8.2, 8.3, 8.4_

  - [x] 4.3 Implementar `print_reflections` e função `main`
    - `print_reflections(classified_tickets, df)` imprime respostas para as 3 perguntas de reflexão baseadas nos dados reais processados, citando exemplos concretos de tickets
    - `main()` orquestra o pipeline completo: carregar → ordenar → extrair → classificar → sugerir → priorizar → gerar JSONs → imprimir reflexões
    - _Requisitos: 10.1, 10.2_

- [x] 5. Integração e validação final
  - [x] 5.1 Conectar todos os componentes no `main()` e validar execução end-to-end
    - Garantir que `main()` executa o pipeline completo com `conversations.csv` e gera os dois arquivos JSON corretamente
    - Verificar que o script pode ser executado via `python ghost_detector.py`
    - _Requisitos: 1.1, 2.1, 3.1, 4.1, 5.1–5.5, 6.1, 7.1–7.5, 8.1, 9.1–9.4, 10.1_

  - [ ]* 5.2 Escrever testes de integração
    - Testar o pipeline completo com o CSV real, verificando que os JSONs gerados contêm todos os tickets com classificações e ações corretas
    - _Requisitos: 6.1, 6.2, 8.1, 8.2, 9.4_

- [x] 6. Checkpoint final — Garantir que todos os testes passam
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

## Notas

- Tarefas marcadas com `*` são opcionais e podem ser puladas para um MVP mais rápido
- Cada tarefa referencia requisitos específicos para rastreabilidade
- Checkpoints garantem validação incremental
- Testes de propriedade validam propriedades universais de corretude das funções puras
- Testes unitários validam exemplos específicos e casos de borda
