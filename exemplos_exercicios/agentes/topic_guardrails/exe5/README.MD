🛡️ Exercício: Guardrails para Recuperação Segura (Proteção de Internal Notes)
📌 Visão Geral

Neste exercício, você irá construir um agente de IA que busca informações no banco de dados (conversations e feedbacks) e aplica guardrails para garantir que conteúdos sensíveis nunca sejam expostos ao usuário.

O sistema contém uma tabela chamada sensitive_items, que representa dados internos (por exemplo, internal notes sobre usuários).

O objetivo é garantir que:

O agente pode acessar dados sensíveis internamente, mas nunca deve expô-los na resposta.

🎯 Objetivo

Construimos um agente que:

Busca dados relevantes no banco
Filtra conteúdos sensíveis ou inseguros
Responde apenas com informações seguras
Bloqueia tentativas de acesso a dados internos
🧱 Dados Disponíveis

Seu banco contém:
conversations - Mensagens entre usuário e suporte

feedbacks - Feedbacks dos usuários

sensitive_items - Dados internos, como:

internal notes - descrições negativas de usuários
conteúdo confidencial

internal notes  nunca devem aparecer na resposta