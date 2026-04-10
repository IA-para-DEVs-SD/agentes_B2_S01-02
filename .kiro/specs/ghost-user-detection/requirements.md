# Documento de Requisitos

## Introdução

Sistema de Detecção de Ghost Users e Ações de Reengajamento. O sistema analisa conversas entre clientes e atendentes a partir de um arquivo CSV, identifica usuários que "sumiram" (ghost users), classifica o estado de cada ticket e sugere ações de reengajamento. Os resultados são exportados em arquivos JSON (`conversation_status.json`, `ticket_actions.json`). Opcionalmente, o sistema atribui prioridades aos tickets.

## Glossário

- **Sistema_Detecção**: O sistema Python responsável por processar o CSV de conversas, classificar tickets e gerar saídas JSON.
- **Ghost_User**: Usuário (cliente) que parou de responder em uma conversa, deixando o atendente como último interlocutor.
- **Ticket**: Unidade de atendimento identificada por `ticket_id`, contendo uma ou mais mensagens entre cliente e atendente.
- **Conversa**: Sequência de mensagens dentro de um ticket, identificada por `conversation_id`.
- **Speaker**: O interlocutor de uma mensagem — pode ser `client` (cliente) ou `atendente`.
- **Status_Final**: O valor de `ticket_status` na última mensagem (ordenada por timestamp) de um ticket.
- **Classificação**: Categoria atribuída a cada ticket com base no último speaker e no status final (`precisa_follow_up`, `encerrado`, `resolvido`, `risco`, `ativo`).
- **Ação_Sugerida**: Ação recomendada para cada ticket com base na classificação (`send_follow_up`, `monitor`, `no_action`).
- **Prioridade**: Nível de urgência atribuído a um ticket (`high`, `medium`, `low`).
- **CSV_Conversas**: Arquivo `conversations.csv` contendo as colunas `ticket_id`, `conversation_id`, `user_id`, `speaker`, `message`, `timestamp`, `ticket_status`.

## Requisitos

### Requisito 1: Carregamento e Validação do CSV

**User Story:** Como desenvolvedor, quero que o sistema carregue e valide o arquivo `conversations.csv`, para que os dados estejam prontos para processamento.

#### Critérios de Aceitação

1. WHEN o arquivo `conversations.csv` é fornecido, THE Sistema_Detecção SHALL carregar os dados em um DataFrame com as colunas `ticket_id`, `conversation_id`, `user_id`, `speaker`, `message`, `timestamp`, `ticket_status`.
2. WHEN o arquivo `conversations.csv` é carregado, THE Sistema_Detecção SHALL converter a coluna `timestamp` para o tipo datetime.
3. IF o arquivo `conversations.csv` não existir no caminho esperado, THEN THE Sistema_Detecção SHALL exibir uma mensagem de erro descritiva e encerrar a execução.
4. IF o arquivo `conversations.csv` contiver colunas ausentes, THEN THE Sistema_Detecção SHALL exibir uma mensagem indicando quais colunas estão faltando.

### Requisito 2: Ordenação dos Dados

**User Story:** Como desenvolvedor, quero que os dados sejam ordenados por conversa e timestamp, para que a análise temporal seja correta.

#### Critérios de Aceitação

1. WHEN os dados são carregados, THE Sistema_Detecção SHALL ordenar as mensagens por `conversation_id` (crescente) e `timestamp` (crescente).
2. THE Sistema_Detecção SHALL preservar todas as mensagens originais após a ordenação, sem perda de dados.

### Requisito 3: Identificação do Último Speaker por Conversa

**User Story:** Como desenvolvedor, quero identificar quem falou por último em cada conversa, para determinar se o cliente sumiu.

#### Critérios de Aceitação

1. WHEN os dados estão ordenados, THE Sistema_Detecção SHALL identificar a última mensagem de cada `conversation_id` com base no `timestamp` mais recente.
2. WHEN a última mensagem é identificada, THE Sistema_Detecção SHALL extrair o valor do campo `speaker` dessa mensagem como o último interlocutor da conversa.
3. THE Sistema_Detecção SHALL retornar o último speaker como `client` ou `atendente` para cada conversa.

### Requisito 4: Identificação do Status Final do Ticket

**User Story:** Como desenvolvedor, quero identificar o status final de cada ticket, para classificar corretamente a situação.

#### Critérios de Aceitação

1. WHEN os dados estão ordenados, THE Sistema_Detecção SHALL identificar a última mensagem de cada `ticket_id` com base no `timestamp` mais recente.
2. WHEN a última mensagem do ticket é identificada, THE Sistema_Detecção SHALL extrair o valor do campo `ticket_status` como o status final do ticket.
3. THE Sistema_Detecção SHALL retornar o status final como um dos valores: `open`, `pending`, `solved` ou `closed`.

### Requisito 5: Classificação dos Tickets

**User Story:** Como desenvolvedor, quero classificar cada ticket com base no último speaker e no status final, para entender a situação de cada atendimento.

#### Critérios de Aceitação

1. WHEN o último speaker é `atendente` e o status final é `pending`, THE Sistema_Detecção SHALL classificar o ticket como `precisa_follow_up`.
2. WHEN o último speaker é `atendente` e o status final é `closed`, THE Sistema_Detecção SHALL classificar o ticket como `encerrado`.
3. WHEN o último speaker é `client` e o status final é `solved`, THE Sistema_Detecção SHALL classificar o ticket como `resolvido`.
4. WHEN o último speaker é `atendente` e o status final é `open`, THE Sistema_Detecção SHALL classificar o ticket como `risco`.
5. WHEN o último speaker é `client` e o status final não é `solved`, THE Sistema_Detecção SHALL classificar o ticket como `ativo`.

### Requisito 6: Geração do Arquivo conversation_status.json

**User Story:** Como desenvolvedor, quero gerar um arquivo JSON com a classificação de cada ticket, para ter uma saída estruturada do processamento.

#### Critérios de Aceitação

1. WHEN todos os tickets são classificados, THE Sistema_Detecção SHALL gerar o arquivo `conversation_status.json` no diretório `exemplos_exercicios/exercicio_2/`.
2. THE Sistema_Detecção SHALL formatar o arquivo como uma lista JSON onde cada elemento contém os campos `ticket_id` (inteiro) e `status` (string com a classificação).
3. THE Sistema_Detecção SHALL incluir exatamente um registro por `ticket_id` no arquivo de saída.
4. WHEN o arquivo `conversation_status.json` é gerado, THE Sistema_Detecção SHALL serializar o JSON com indentação de 2 espaços e encoding UTF-8 para suportar caracteres especiais.

### Requisito 7: Sugestão de Ações por Ticket

**User Story:** Como desenvolvedor, quero que o sistema sugira ações para cada ticket, para orientar o time de atendimento.

#### Critérios de Aceitação

1. WHEN a classificação de um ticket é `precisa_follow_up`, THE Sistema_Detecção SHALL sugerir a ação `send_follow_up`.
2. WHEN a classificação de um ticket é `risco`, THE Sistema_Detecção SHALL sugerir a ação `monitor`.
3. WHEN a classificação de um ticket é `encerrado`, THE Sistema_Detecção SHALL sugerir a ação `no_action`.
4. WHEN a classificação de um ticket é `resolvido`, THE Sistema_Detecção SHALL sugerir a ação `no_action`.
5. WHEN a classificação de um ticket é `ativo`, THE Sistema_Detecção SHALL sugerir a ação `no_action`.

### Requisito 8: Geração do Arquivo ticket_actions.json

**User Story:** Como desenvolvedor, quero gerar um arquivo JSON com as ações sugeridas, para que o time de atendimento tenha orientações claras.

#### Critérios de Aceitação

1. WHEN todas as ações são determinadas, THE Sistema_Detecção SHALL gerar o arquivo `ticket_actions.json` no diretório `exemplos_exercicios/exercicio_2/`.
2. THE Sistema_Detecção SHALL formatar o arquivo como uma lista JSON onde cada elemento contém os campos `ticket_id` (inteiro) e `action` (string com a ação sugerida).
3. THE Sistema_Detecção SHALL incluir exatamente um registro por `ticket_id` no arquivo de saída.
4. WHEN o arquivo `ticket_actions.json` é gerado, THE Sistema_Detecção SHALL serializar o JSON com indentação de 2 espaços e encoding UTF-8.

### Requisito 9: Sistema de Prioridades (Desafio Opcional)

**User Story:** Como desenvolvedor, quero atribuir prioridades aos tickets, para que o time saiba quais atendimentos tratar primeiro.

#### Critérios de Aceitação

1. WHEN a classificação é `risco` (ghost user + status open), THE Sistema_Detecção SHALL atribuir prioridade `high` ao ticket.
2. WHEN o status final é `pending`, THE Sistema_Detecção SHALL atribuir prioridade `medium` ao ticket.
3. WHEN o status final é `closed` ou `solved`, THE Sistema_Detecção SHALL atribuir prioridade `low` ao ticket.
4. WHEN as prioridades são atribuídas, THE Sistema_Detecção SHALL incluir o campo `priority` no arquivo `ticket_actions.json` para cada ticket.

### Requisito 10: Respostas de Reflexão

**User Story:** Como desenvolvedor, quero que o sistema gere respostas para as perguntas de reflexão, para documentar o entendimento do problema.

#### Critérios de Aceitação

1. THE Sistema_Detecção SHALL imprimir no console as respostas para as três perguntas de reflexão: (a) se todo ghost precisa de follow-up, (b) quando é melhor encerrar um ticket, (c) se o status do sistema sempre reflete o comportamento do usuário.
2. THE Sistema_Detecção SHALL basear as respostas de reflexão nos dados reais processados do CSV, citando exemplos concretos dos tickets analisados.
