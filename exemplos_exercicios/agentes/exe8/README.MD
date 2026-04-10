
Exercício: Enriquecendo dados internos com busca externa

Objetivo

Criar um fluxo em que o sistema:

analisa dados internos do banco
identifica os tópicos mais recorrentes
usa uma tool externa para buscar conteúdo complementar
organiza os resultados para apoiar análise ou suporte
Cenário

Você tem duas tabelas no banco:

conversations
feedbacks

Essas tabelas contêm reclamações, dúvidas e feedbacks de usuários.

Seu trabalho será:

identificar os temas mais frequentes
buscar artigos externos sobre esses temas usando Exa
salvar esses arquivos como .txt na pasta exe8/arquivos
O que os alunos devem construir
Parte 1 — identificar temas frequentes

Criar uma função que analise conversations ou feedbacks e encontre os assuntos mais recorrentes.

Exemplo de temas:

login
pagamento
lentidão
travamento
entrega
cancelamento

Eles podem fazer isso por palavras-chave.

Exemplo:

def get_top_topics(feedbacks_df) -> list[tuple[str, int]]:
    ...

Saída esperada:

[
    ("pagamento", 8),
    ("login", 6),
    ("lentidão", 5)
]
Parte 2 — criar a tool externa

Criar uma tool com Exa para buscar artigos relacionados a cada tema.

Exemplo:

def search_external_articles(topic: str) -> list[dict]:
    ...

Saída esperada:

[
    {
        "topic": "pagamento",
        "title": "Common Causes of Payment Failures",
        "url": "...",
        "text": "..."
    }
]
Parte 3 — enriquecer os tópicos

Para cada tópico frequente, buscar 2 ou 3 artigos externos.

Exemplo:

def enrich_topics_with_external_articles(topics: list[str]) -> dict:
    ...

Saída esperada:

{
    "pagamento": [...],
    "login": [...],
    "lentidão": [...]
}
Parte 4 — exibir resultado

Mostrar algo como:

Tópicos mais frequentes:
1. pagamento (8)
2. login (6)
3. lentidão (5)

Artigos externos encontrados:

[pagamento]
- ...
- ...

[login]
- ...
- ...

[lentidão]
- ...
- ...