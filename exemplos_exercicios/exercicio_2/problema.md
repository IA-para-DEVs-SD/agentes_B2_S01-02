# 🧪 Exercício — Detecção de Ghost Users e Ações de Reengajamento

## 🎯 Objetivo

Construir um sistema capaz de:

* Analisar conversas entre cliente e atendente
* Identificar usuários que “sumiram” (ghost)
* Entender o estado do ticket
* Sugerir ações de reengajamento


## 📊 Dataset

Arquivo: `conversations.csv`

Colunas:

* `ticket_id`
* `conversation_id`
* `user_id`
* `speaker` (client / atentende)
* `message`
* `timestamp`
* `ticket_status` (open, pending, solved, closed)



## 🧠 Parte 1 — Entendimento

Antes de programar, responda:

1. O que é um **ghost user**?
2. Quando um ticket pode ser considerado **resolvido**?
3. Quando vale a pena fazer **follow-up**?



## ⚙️ Parte 2 — Processamento

### 1. Ordenar os dados

* Ordenar por `conversation_id` e `timestamp`



### 2. Identificar o último speaker por conversa

Para cada `conversation_id`:

* Quem falou por último?

  * `client`
  * `atendente`



### 3. Identificar status final do ticket

Para cada `ticket_id`:

* Qual é o último `ticket_status`?



## 🧪 Parte 3 — Classificação

Classifique cada conversa em uma das categorias:

| Condição                         | Classificação     |
| -------------------------------- | ----------------- |
| Agent falou por último + pending | precisa_follow_up |
| Agent falou por último + closed  | encerrado         |
| Client respondeu + solved        | resolvido         |
| Agent falou por último + open    | risco             |
| Client respondeu recentemente    | ativo             |



## 📄 Parte 4 — Saída

Gerar arquivo:

### `conversation_status.json`

```json
[
  {
    "ticket_id": 1001,
    "status": "encerrado"
  }
]
```



##  Parte 5 — Comportamento de Assistente

Agora o sistema deve **sugerir ações**.



### Regra de decisão

Para cada ticket:

| Situação          | Sugestão/Ação  |
| ----------------- | -------------- |
| precisa_follow_up | send_follow_up |
| risco             | monitor        |
| encerrado         | no_action      |
| resolvido         | no_action      |



### Gerar arquivo:

## `ticket_actions.json`

```json
[
  {
    "ticket_id": 1005,
    "action": "send_follow_up"
  }
]
```



## 🧠 Parte 6 — Reflexão

Responda:

* Todo ghost precisa de follow-up?
* Quando é melhor encerrar um ticket?
* O status do sistema sempre reflete o comportamento do usuário?



## 🔥 Desafio (Opcional)

1. Priorize os tickets:

| Regra        | Prioridade |
| ------------ | ---------- |
| ghost + open | high       |
| pending      | medium     |
| closed       | low        |



2. Gere:

```json
{
  "ticket_id": 1005,
  "priority": "high"
}
```

