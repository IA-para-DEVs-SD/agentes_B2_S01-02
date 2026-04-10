Objetivo

Criar um mecanismo de guardrail que valide uma internal note antes de salvar no banco.

O sistema deve impedir que notas com:

- PII
- linguagem negativa ou pejorativa sobre o usuário

sejam salvas normalmente.

O que vocês devem construir

Vocês deverão criar uma solução com os seguintes componentes:

1. Tabela no banco

Já está no init.sql, se precisar rode docker compose down, docker compose up -d 
(load_data.py para trazer os dados novamente)

2. Função de validação

Criar uma função que receba o texto da nota e verifique se ela contém:

PII

Exemplos:

email
telefone
CPF ou outro identificador numérico
Conteúdo negativo

Exemplos:

“difficult user”
“rude”
“hostile”
“aggressive”
“manipulative”

3. Regra de decisão

Ao tentar salvar uma nota, o sistema deve decidir entre um destes comportamentos:

Opção mínima obrigatória
saved
blocked
Opção melhorada
saved
sanitized_and_saved
blocked
Regras esperadas

Caso 1 — nota segura

Entrada:

Customer reported login failure after password reset.

Resultado esperado:

saved

Caso 2 — nota com julgamento negativo

Entrada:

This is a difficult user and complains frequently.

Resultado esperado:

blocked

ou, se implementarem sanitização:

sanitized_and_saved
Caso 3 — nota com PII

Entrada:

Customer email is joao.silva@email.com and asked for an update.

Resultado esperado:

blocked

ou:

sanitized_and_saved
Caso 4 — nota com dois problemas

Entrada:

This rude customer called again. Phone: 41999998888

Resultado esperado:

o sistema deve detectar PII
o sistema deve detectar linguagem inadequada
a nota não deve ser salva como se estivesse correta