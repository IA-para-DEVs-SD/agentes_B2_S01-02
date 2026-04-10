EXA Tool — O que essa tool faz?
📌 Visão Geral

A função search_external é uma tool de busca externa que permite ao agente acessar informações fora do banco de dados, utilizando a API do Exa.

Ela simula o comportamento de um agente que consegue “pesquisar na internet”.

🧠 Objetivo

Permitir que o agente:

busque informações atualizadas
complemente dados internos
responda perguntas que não estão no banco
⚙️ Como funciona
1. Autenticação

A tool usa uma chave de API:

EXA_API_KEY = os.getenv("EXA_API_KEY")

Essa chave permite acessar o serviço do Exa.

2. Criação do cliente
exa = Exa(EXA_API_KEY)

Aqui criamos o cliente que faz a comunicação com a API.

3. Busca de conteúdo
response = exa.search_and_contents(
    query,
    num_results=5,
    use_autoprompt=True,
    text=True
)

Essa chamada:

recebe uma consulta (query)
busca conteúdos relevantes na web
retorna resultados com texto e metadados
4. Estrutura dos resultados

Cada resultado é transformado em um dicionário:

{
    "source": "external",
    "title": item.title,
    "text": item.text,
    "url": item.url
}
📦 Saída da função

A função retorna uma lista:

[
    {
        "source": "external",
        "title": "Login troubleshooting guide",
        "text": "...",
        "url": "https://..."
    }
]