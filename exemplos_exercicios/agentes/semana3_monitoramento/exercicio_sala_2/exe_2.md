# Exercícios: Comparação com MLflow

## Exercício 2.1 — Engenharia de Prompts

### Contexto
Você foi contratado para construir um agente que responde dúvidas de clientes de um e-commerce. O time de produto quer saber qual estilo de prompt gera respostas melhores — mas antes de perguntar para os clientes, querem dados.
### Objetivo
Comparar 3 versões de system prompt e medir o impacto em tokens e qualidade das respostas.
Variações a testar
VARIACOES = [

    {"system_prompt": "Você é um atendente de e-commerce. Responda de forma objetiva."},

    {"system_prompt": "Você é um atendente de e-commerce simpático. Use linguagem informal e emojis."},

    {"system_prompt": "Você é um especialista em e-commerce. Dê respostas detalhadas com exemplos práticos."},

]


Perguntas de teste (use as mesmas para todas as variações)
PERGUNTAS = [

    "Meu pedido não chegou, o que eu faço?",

    "Vocês aceitam devolução?",

    "Como rastreio minha entrega?",

]

### O que registrar no MLflow
system_prompt como param
tokens_medio e latencia_media como métricas
tokens_por_pergunta com step para ver a evolução

### Bônus
Adicione um LLM-as-a-Judge que avalia a satisfação do cliente com a resposta (score de 0 a 1) e registre como métrica judge_score no MLflow.


## Exercício 2.2 — Benchmark de Modelos

### Contexto
Sua empresa quer adotar um agente de IA para responder perguntas técnicas de suporte. O time de engenharia precisa decidir entre dois modelos da Anthropic antes de ir para produção. Você precisa gerar dados para embasar a decisão.
Objetivo
Comparar claude-haiku-4-5 vs claude-opus-4-5 em custo (tokens), velocidade (latência) e qualidade (judge score).
Variações a testar
VARIACOES = [

    {"model": "claude-haiku-4-5"},

    {"model": "claude-opus-4-5"},

]
Perguntas de teste
PERGUNTAS = [

    "Como faço para resetar minha senha via API?",

    "Qual a diferença entre autenticação OAuth e API Key?",

    "Minha requisição está retornando erro 429, o que significa?",

]

### O que registrar no MLflow
model como param
tokens_medio, latencia_media como métricas
judge_score_medio como métrica (obrigatório neste exercício)

### Judge obrigatório
Crie um LLM-as-a-Judge que avalia a precisão técnica da resposta:

Você é um engenheiro sênior avaliando respostas de suporte técnico.

Pergunta: {pergunta}

Resposta: {resposta}

A resposta é tecnicamente correta e útil para um desenvolvedor?

- Score 1.0: correta, clara e completa

- Score 0.5: parcialmente correta ou incompleta

- Score 0.0: incorreta ou confusa

Responda APENAS com JSON: {"score": 0.0, "justificativa": "..."}

#### Bônus
Adicione um terceiro modelo de outro vendor (ex: OpenAI ou Gemini) e refaça a comparação.


💡 Dica para os dois exercícios
O arquivo 3_mlflow/ml_flow_example.py já tem a estrutura pronta. Você só precisa:

1 - Trocar o VARIACOES
2 - Trocar as PERGUNTAS
3- Ajustar o EXPERIMENTO_NOME

O restante do código funciona igual para qualquer variação.
