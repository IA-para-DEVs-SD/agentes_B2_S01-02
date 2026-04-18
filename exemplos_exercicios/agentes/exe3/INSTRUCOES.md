# Exercício 3 - Análise de Feedbacks com Gemini

## Status da Implementação

✅ Tabela `feedback_analysis` criada no banco de dados
✅ 5 tools implementadas seguindo o padrão do exe2
✅ Agente com tool calling do Gemini configurado
✅ Script de teste criado
✅ Processamento individual por feedback_id (fins didáticos)

## Estrutura do Projeto

```
exe3/
├── tools.py                    # 5 tools para análise de feedbacks
├── feedback_agent.py           # Agente com tool calling do Gemini
├── run_feedback_agent.py       # Script principal de execução
├── test_tools.py              # Script de teste das tools
└── README.md                   # Enunciado original do exercício
```

## Tools Implementadas

### 1. `get_feedback(feedback_id)`
Busca um feedback específico pelo ID do banco de dados.

### 2. `analyze_feedback_with_llm(feedback_text)`
Analisa o feedback usando Gemini e retorna:
- categoria (bug, elogio, pagamento, performance, atendimento, outros)
- sentimento (positivo, negativo, neutro)
- resumo (frase curta)

### 3. `classify_feedback(categoria, sentimento)`
Adiciona classificações adicionais:
- prioridade (alta, média, baixa)
- requer_acao (boolean)

### 4. `save_analysis_results(feedback_id, analysis)`
Salva o resultado da análise na tabela `feedback_analysis` (com UPSERT).

### 5. `generate_final_report()`
Gera relatório consolidado com estatísticas de todos os feedbacks já analisados.

## Como Usar

### 1. Configure a chave da API do Gemini

Edite o arquivo `.env` na raiz do projeto e adicione sua chave:

```env
GEMINI_API_KEY='sua-chave-aqui'
```

Obtenha sua chave em: https://aistudio.google.com/app/apikey

### 2. Liste os feedbacks disponíveis

```bash
python exemplos_exercicios/agentes/exe3/list_feedbacks.py
```

Este script mostra todos os feedbacks disponíveis no banco (IDs de 1 a 30).

### 3. Teste as tools básicas

```bash
python exemplos_exercicios/agentes/exe3/test_tools.py 1
```

Este script testa a conexão com o banco e a leitura de um feedback específico.

### 4. Execute o agente para analisar um feedback

```bash
python exemplos_exercicios/agentes/exe3/run_feedback_agent.py 1
```

O agente irá:
1. Buscar o feedback com ID especificado
2. Analisar com o Gemini (categoria, sentimento, resumo)
3. Classificar e adicionar prioridade
4. Salvar os resultados no banco

### 5. Analise múltiplos feedbacks

Para analisar vários feedbacks, execute o comando para cada um:

```bash
python exemplos_exercicios/agentes/exe3/run_feedback_agent.py 1
python exemplos_exercicios/agentes/exe3/run_feedback_agent.py 2
python exemplos_exercicios/agentes/exe3/run_feedback_agent.py 3
```

### 6. Gere o relatório consolidado

Após analisar vários feedbacks, você pode gerar um relatório consolidado executando o agente com qualquer ID e pedindo para gerar o relatório, ou consultando diretamente o banco.

## Tabela de Análise

A tabela `feedback_analysis` foi criada com a seguinte estrutura:

```sql
CREATE TABLE feedback_analysis (
    feedback_id INT PRIMARY KEY,
    categoria VARCHAR(50),
    sentimento VARCHAR(20),
    resumo TEXT,
    prioridade VARCHAR(20),
    requer_acao BOOLEAN,
    analyzed_at TIMESTAMP
);
```

## Fluxo do Agente (por feedback)

O agente usa tool calling do Gemini para executar as seguintes etapas:

1. **Buscar feedback**: Chama `get_feedback(feedback_id)` para obter os dados
2. **Analisar com LLM**: Chama `analyze_feedback_with_llm(feedback_text)` para análise
3. **Classificar**: Chama `classify_feedback(categoria, sentimento)` para adicionar prioridade
4. **Salvar**: Combina os resultados e chama `save_analysis_results(feedback_id, analysis)`

## Exemplo de Saída Individual

```json
{
  "feedback_id": 1,
  "categoria": "bug",
  "sentimento": "negativo",
  "resumo": "Usuário relatou falha ao acessar a tela de pagamento",
  "prioridade": "alta",
  "requer_acao": true
}
```

## Exemplo de Relatório Consolidado

```json
{
  "total_feedbacks": 10,
  "categorias": {
    "bug": 3,
    "performance": 2,
    "pagamento": 1,
    "elogio": 2,
    "atendimento": 1,
    "outros": 1
  },
  "sentimentos": {
    "negativo": 6,
    "positivo": 3,
    "neutro": 1
  },
  "prioridades": {
    "alta": 4,
    "média": 3,
    "baixa": 3
  },
  "feedbacks_requerem_acao": 4,
  "principais_pontos": [
    "Identificados 3 relatos de bugs técnicos",
    "Usuários reportaram 2 problemas de performance",
    "Há 1 feedbacks sobre problemas de pagamento",
    "Recebemos 2 elogios dos usuários",
    "Sentimento predominantemente negativo - atenção necessária",
    "4 feedbacks requerem ação imediata"
  ]
}
```

## Diferenças do exe2

- **exe2**: Processa tickets de suporte com conversas
- **exe3**: Processa feedbacks individuais de usuários
- **exe2**: Foco em classificação e follow-up
- **exe3**: Foco em análise de sentimento e priorização
- **Ambos**: Processam um item por vez (passado como parâmetro)

## Consultar Resultados no Banco

```sql
-- Ver todos os feedbacks analisados
SELECT * FROM feedback_analysis ORDER BY feedback_id;

-- Ver feedbacks que requerem ação
SELECT * FROM feedback_analysis WHERE requer_acao = true;

-- Ver feedbacks por prioridade
SELECT * FROM feedback_analysis WHERE prioridade = 'alta';

-- Ver feedbacks por categoria
SELECT categoria, COUNT(*) as total 
FROM feedback_analysis 
GROUP BY categoria;
```
