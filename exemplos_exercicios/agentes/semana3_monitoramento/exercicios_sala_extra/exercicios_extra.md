# 🧪 Exercícios Avançados: Monitoramento de Agentes em Produção

## Exercício 3 — Detecção de Regressão

###  Contexto

Imagine que você trabalha no time de IA de um e-commerce. Vocês têm um agente de atendimento ao cliente rodando em produção há 3 meses. O time de produto pediu para melhorar o tom das respostas — o agente estava sendo muito seco com os clientes.

Você atualiza o system prompt e faz um teste rápido: parece melhor! Você faz o deploy.

Dois dias depois, o suporte começa a receber reclamações. Os clientes dizem que o agente está dando informações erradas sobre prazo de devolução.

**O que aconteceu?** Ao mudar o tom, você inadvertidamente mudou também o comportamento do agente. Mas você não tinha como saber — porque não estava comparando com uma base fixa.

Esse problema tem nome: **regressão**. E a solução é um **dataset de avaliação**.

---

### O que é um Dataset de Avaliação?

É uma coleção fixa de pares `pergunta → resposta esperada` que representa o comportamento correto do seu agente. Ele não muda — é a sua "régua" de qualidade.

```python
DATASET = [
    {
        "pergunta": "Qual o prazo de devolução?",
        "resposta_esperada": "O prazo de devolução é de 30 dias após a compra."
    },
    {
        "pergunta": "Como rastreio minha entrega?",
        "resposta_esperada": "Acesse o site com o código de rastreio enviado por email."
    },
]
```

Toda vez que você mudar algo no agente (prompt, modelo, ferramentas), você roda o agente no mesmo dataset e compara os scores:

```
prompt v1 → score médio: 0.85  ✅
prompt v2 → score médio: 0.60  ⚠️ REGRESSÃO DETECTADA
```

Com isso, você detecta o problema **antes** de fazer o deploy — não depois de receber reclamações.



###  Objetivo

Criar um dataset fixo de 5 perguntas com respostas esperadas, rodar o agente com 2 versões de prompt diferentes, e usar um LLM-as-a-Judge para detectar qual versão causou regressão.



###  O que construir

**1. Dataset fixo:**
```python
DATASET = [
    {"pergunta": "...", "resposta_esperada": "..."},
    # 5 itens no total — você define o tema (e-commerce, suporte técnico, etc.)
]
```

**2. Judge de similaridade** — avalia o quão próxima a resposta do agente está da resposta esperada:
```
Score 1.0 → resposta correta e completa
Score 0.5 → parcialmente correta
Score 0.0 → incorreta ou contradiz a resposta esperada
```

**3. Duas variações de prompt** para comparar:
```python
VARIACOES = [
    {"nome": "formal", "system_prompt": "Responda de forma formal e técnica."},
    {"nome": "casual", "system_prompt": "Responda de forma casual e simpática."},
]
```

**4. Registrar no MLflow:**
- `judge_score_medio` por variação
- `judge_por_pergunta` com step (para ver qual pergunta regrediu)


### Bônus
Registre o dataset no Langfuse usando `langfuse.api.datasets.create()` e vincule cada execução a um item do dataset.



## Exercício 4 — Monitor de Latência e Qualidade

### Contexto

Seu agente está em produção. Tudo parece bem — mas "parece" não é suficiente. Você precisa de dados.

Pense em como funciona o monitoramento de um servidor web: ninguém fica olhando o dashboard 24 horas por dia. Em vez disso, você configura **alertas** — se o servidor demorar mais de 2 segundos para responder, ou se a taxa de erro passar de 1%, você recebe uma notificação.

Com agentes de LLM, a lógica é a mesma. Só que os indicadores são diferentes:

- **Latência** → quanto tempo o agente demora para responder
- **Qualidade** → o judge score está caindo?
- **Custo** → os tokens estão aumentando sem motivo?

Se qualquer um desses indicadores sair do normal, você quer saber **agora** — não na próxima reunião de segunda-feira.

---

### O que são Thresholds?

Threshold (ou limiar) é o valor a partir do qual algo vira um problema. Você define com base no seu SLA (acordo de nível de serviço) ou na experiência com o sistema.

Exemplos:
```
latência > 3s        → usuário começa a desistir
judge score < 0.6    → qualidade abaixo do aceitável
total_tokens > 2000  → custo acima do esperado por pergunta
```

Quando um threshold é violado, você dispara um **alerta** — que pode ser um log, um email, uma mensagem no Slack, ou um PagerDuty em casos críticos.


###  Objetivo

Adicionar um sistema de monitoramento ao agente que detecta automaticamente quando a latência ou a qualidade estão fora do esperado, registra os alertas e os expõe como métricas no MLflow.



### O que construir

**1. Thresholds configuráveis:**
```python
THRESHOLDS = {
    "latencia_max_segundos": 3.0,
    "judge_score_minimo": 0.6,
    "tokens_max_por_resposta": 1500,
}
```

**2. Função de verificação após cada resposta:**
```python
def verificar_alertas(metricas: dict, thresholds: dict) -> list[str]:
    alertas = []
    if metricas["latency_seconds"] > thresholds["latencia_max_segundos"]:
        alertas.append(f"⚠️ LATÊNCIA ALTA: {metricas['latency_seconds']}s")
    if metricas["judge_score"] < thresholds["judge_score_minimo"]:
        alertas.append(f"⚠️ QUALIDADE BAIXA: score {metricas['judge_score']}")
    return alertas
```

**3. Log de alertas em arquivo** (`alertas.log`):
```
2026-04-24 17:32:10 | LATÊNCIA ALTA | 4.2s | pergunta: "Como cancelo meu pedido?"
2026-04-24 17:32:45 | QUALIDADE BAIXA | score 0.4 | pergunta: "Qual o prazo de entrega?"
```

**4. Registrar no MLflow:**
- `alertas_disparados` (total de alertas no run)
- `alertas_latencia` e `alertas_qualidade` separados



###  Bônus
Simule um alerta de Slack imprimindo a mensagem formatada no terminal:
```
🚨 [ALERTA SLACK] #monitoramento-agente
Latência alta detectada: 4.2s (threshold: 3.0s)
Pergunta: "Como cancelo meu pedido?"
Run MLflow: agent-1745510400
```



## Exercício 5 — Relatório Automático de Experimento

### Contexto

Você rodou seus experimentos, coletou as métricas, e agora precisa apresentar os resultados para o time de produto. O CTO quer uma recomendação clara: **qual modelo usar em produção?**

Você poderia abrir o MLflow e tirar prints. Mas isso não é escalável — e não é o que um engenheiro de produção faz.

Em times de ML maduros, o relatório de experimento é **gerado automaticamente** ao final de cada rodada de testes. Ele inclui tabelas comparativas, gráficos, e uma recomendação baseada nos dados. O engenheiro revisa e aprova — mas não escreve do zero.

Isso tem um nome: **MLOps**. E o que você vai construir nesse exercício é uma versão simplificada desse pipeline.



###  Por que o LLM gera a recomendação?

Porque o LLM é bom em sintetizar dados e escrever texto estruturado. Em vez de você escrever:

> *"O modelo claude-haiku-4-5 apresentou latência média de 1.2s e judge score de 0.82, enquanto o claude-opus-4-5 apresentou latência de 3.4s e judge score de 0.91. Considerando o custo-benefício..."*

Você passa os dados para o LLM e ele escreve isso por você — com base nos números reais do experimento.

```python
prompt = f"""
Você é um engenheiro de ML sênior. Analise os resultados abaixo e escreva
uma recomendação de 2 parágrafos sobre qual modelo usar em produção.

Dados do experimento:
{json.dumps(resultados, indent=2)}

Critérios de decisão: qualidade (judge score) tem peso 60%, custo (tokens) tem peso 40%.
"""
```

---

### Objetivo

Rodar 3 variações de experimento (modelo ou prompt), coletar as métricas, e gerar automaticamente um relatório completo em Markdown com tabela comparativa, gráfico de barras e recomendação escrita pelo LLM.



### O que construir

**1. Rodar 3 variações** (você escolhe — modelos, prompts ou temperaturas)

**2. Gerar tabela comparativa em Markdown:**
```markdown
| Modelo | Tokens Médio | Latência Média | Judge Score |
|--------|-------------|----------------|-------------|
| haiku  | 450         | 1.2s           | 0.82        |
| opus   | 890         | 3.4s           | 0.91        |
```

**3. Gerar gráfico de barras** com matplotlib comparando `judge_score_medio` por variação e salvar como `grafico.png`

**4. Gerar recomendação com LLM** — passa os dados como JSON e pede uma análise escrita

**5. Salvar tudo em `relatorio.md`:**
```markdown
# Relatório de Experimento — 2026-04-24

## Resultados
[tabela]

## Análise
[texto gerado pelo LLM]
```


### Bônus
Adicione ao relatório uma seção de **riscos** — peça para o LLM identificar possíveis problemas com a opção recomendada:
```
## Riscos da Recomendação
[LLM analisa trade-offs e aponta o que pode dar errado]
```

---

## Dicas Gerais

Para os 3 exercícios, o arquivo `3_mlflow/ml_flow_example.py` que já temos é o ponto de partida. A estrutura base não muda — o que muda é o que você faz **com os resultados** após cada run.

Ordem sugerida para implementar:
1. Faça o agente rodar e coletar métricas 
2. Adicione o judge 
3. Adicione a feature nova do exercício (regressão / alertas / relatório)
4. Teste forçando casos extremos (sleep para latência, prompt ruim para qualidade baixa)