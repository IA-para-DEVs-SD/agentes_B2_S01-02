#O problema

Você quer construir um agente de suporte que consiga:

Entender o problema do usuário
Usar contexto quando existir (histórico)
Buscar informação relevante (KB / RAG)
Responder de forma útil e consistente

Mas isso não é trivial porque:

## 1. Nem sempre existe histórico

Às vezes você recebe:

"não consigo entrar"

👉 sem contexto nenhum

Outras vezes:

ticket_id=1001 → já tem conversa anterior

👉 com contexto rico

##  2. A estratégia muda dependendo do contexto

Você precisa decidir:

uso histórico? → análise mais completa
não uso histórico? → análise rápida

👉 esse é um problema de orquestração de decisão

##  3. O LLM sozinho não resolve tudo

Se você só fizer:

LLM("responda isso")

Você perde:

consistência
controle
integração com dados reais
capacidade de debug

👉 então você precisa quebrar em tools

##  4. O conhecimento não está no LLM

As respostas certas estão em:

base interna (Postgres)
KB (Qdrant / embeddings)

👉 então você precisa de RAG

##  5. Não é só responder — é seguir um fluxo

Você precisa:

classificar
entender
buscar
decidir ação
responder

👉 isso é um pipeline, não uma chamada única

##  Resumo do problema

Como construir um agente que consiga adaptar sua estratégia (com ou sem histórico), integrar dados estruturados e conhecimento vetorial, e ainda gerar respostas úteis e consistentes?

## A resolução contém:

### 1. Decisão de modo
com histórico vs sem histórico
### 2. Análise com LLM
classificação
resumo
ação
### 3. Recuperação (RAG)
embeddings
Qdrant
KB correta
### 4. Orquestração
fluxo controlado
fallback
lógica explícita
### 5. Geração final
resposta para cliente
resumo interno