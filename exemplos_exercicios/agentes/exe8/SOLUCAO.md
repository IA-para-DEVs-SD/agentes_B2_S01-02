# Solução do Exercício 8 - Enriquecimento de Dados com Busca Externa

## 📌 Visão Geral

Sistema completo que analisa dados internos, identifica tópicos frequentes e enriquece com artigos externos usando Exa AI.

## ✅ Implementação Completa

### Fluxo do Sistema

```
1. Analisar dados internos (conversations + feedbacks)
   ↓
2. Identificar tópicos mais frequentes
   ↓
3. Buscar artigos externos com Exa
   ↓
4. Salvar artigos como .txt
   ↓
5. Exibir resultados consolidados
```

## 📁 Arquivos Criados

```
exe8/
├── topic_analyzer.py       # Parte 1: Análise de tópicos
├── external_search.py      # Parte 2: Busca externa com Exa
├── topic_enrichment.py     # Parte 3: Enriquecimento de tópicos
├── main.py                 # Parte 4: Script principal
├── arquivos/               # Diretório com artigos salvos
│   ├── login.txt
│   ├── pagamento.txt
│   ├── lentidão.txt
│   └── ...
└── SOLUCAO.md             # Esta documentação
```

## 🎯 Funcionalidades Implementadas

### Parte 1: Análise de Tópicos

**Arquivo:** `topic_analyzer.py`

- ✅ Extração de palavras-chave de mensagens
- ✅ Análise de conversations e feedbacks
- ✅ Contagem de frequência de tópicos
- ✅ Identificação dos tópicos mais recorrentes

**Tópicos detectados:**
- login, pagamento, lentidão, travamento
- entrega, cancelamento, atendimento
- interface, bug, elogio

### Parte 2: Busca Externa

**Arquivo:** `external_search.py`

- ✅ Integração com Exa AI
- ✅ Queries otimizadas por tópico
- ✅ Busca de artigos relevantes
- ✅ Tratamento de erros

### Parte 3: Enriquecimento

**Arquivo:** `topic_enrichment.py`

- ✅ Enriquecimento de múltiplos tópicos
- ✅ Salvamento de artigos em .txt
- ✅ Organização por tópico
- ✅ Criação automática de diretórios

### Parte 4: Visualização

**Arquivo:** `main.py`

- ✅ Fluxo completo automatizado
- ✅ Exibição organizada de resultados
- ✅ Estatísticas consolidadas
- ✅ Interface interativa

## 🚀 Como Usar

### Pré-requisitos

1. Banco de dados PostgreSQL rodando
2. Chave EXA_API_KEY configurada no .env
3. Bibliotecas instaladas (pandas, sqlalchemy, exa-py)

### Executar Análise Completa

```bash
python exemplos_exercicios/agentes/exe8/main.py
```

Este script executa todo o fluxo automaticamente.

### Executar Partes Individuais

**Apenas análise de tópicos:**
```bash
python exemplos_exercicios/agentes/exe8/topic_analyzer.py
```

**Apenas busca externa:**
```bash
python exemplos_exercicios/agentes/exe8/external_search.py
```

**Apenas enriquecimento:**
```bash
python exemplos_exercicios/agentes/exe8/topic_enrichment.py
```

## 📊 Exemplo de Saída

```
============================================================
📊 TÓPICOS MAIS FREQUENTES
============================================================

 1. lentidão        (15 ocorrências)
 2. pagamento       (12 ocorrências)
 3. login           (10 ocorrências)
 4. travamento      (8 ocorrências)
 5. elogio          (7 ocorrências)

============================================================
📝 EXEMPLOS DE MENSAGENS DOS USUÁRIOS
============================================================

[LENTIDÃO]
  1. "O sistema está muito lento para carregar minhas informações..."
  2. "App muito lento..."

[PAGAMENTO]
  1. "Não consegui finalizar minha compra no site..."
  2. "Pagamento recusado sem motivo aparente..."

[LOGIN]
  1. "Não consigo fazer login na minha conta..."
  2. "Esqueci minha senha e não consigo resetar..."

============================================================
🌐 ARTIGOS EXTERNOS ENCONTRADOS
============================================================

[LENTIDÃO]

  1. How to Fix Slow Performance Issues
     URL: https://example.com/slow-performance
     Preview: Learn how to diagnose and fix slow performance in applications...

  2. Optimizing App Speed - Best Practices
     URL: https://example.com/optimization
     Preview: Top 10 techniques to improve application speed and responsiveness...

[PAGAMENTO]

  1. Common Payment Failures and Solutions
     URL: https://example.com/payment-issues
     Preview: Understanding why payments fail and how to resolve them...

  2. Payment Gateway Troubleshooting Guide
     URL: https://example.com/payment-gateway
     Preview: Complete guide to troubleshooting payment gateway errors...

============================================================
📈 ESTATÍSTICAS
============================================================

  • Tópicos identificados: 5
  • Total de ocorrências: 52
  • Artigos externos encontrados: 10
  • Arquivos salvos: 5

============================================================
```

## 📄 Formato dos Arquivos Salvos

Cada arquivo `.txt` contém:

```
TÓPICO: PAGAMENTO
============================================================

ARTIGO 1
------------------------------------------------------------
Título: Common Payment Failures and Solutions
URL: https://example.com/payment-issues

Conteúdo:
Understanding why payments fail and how to resolve them...
[texto completo do artigo]

============================================================

ARTIGO 2
------------------------------------------------------------
...
```

## 🔍 Funções Principais

### `get_top_topics(limit=10)`

Retorna os tópicos mais frequentes.

```python
from topic_analyzer import get_top_topics

topics = get_top_topics(limit=5)
# [("lentidão", 15), ("pagamento", 12), ...]
```

### `search_external_articles(topic, num_results=3)`

Busca artigos externos para um tópico.

```python
from external_search import search_external_articles

articles = search_external_articles("login", num_results=2)
# [{"topic": "login", "title": "...", "url": "...", "text": "..."}]
```

### `enrich_topics_with_external_articles(topics, articles_per_topic=3)`

Enriquece múltiplos tópicos com artigos.

```python
from topic_enrichment import enrich_topics_with_external_articles

enriched = enrich_topics_with_external_articles(["login", "pagamento"])
# {"login": [...], "pagamento": [...]}
```

### `save_articles_to_files(enriched_data, output_dir)`

Salva artigos em arquivos .txt.

```python
from topic_enrichment import save_articles_to_files

save_articles_to_files(enriched_data)
# Cria arquivos em exe8/arquivos/
```

## 🎓 Conceitos Aplicados

1. **Análise de texto** com extração de palavras-chave
2. **Agregação de dados** de múltiplas fontes
3. **Integração com API externa** (Exa)
4. **Persistência de dados** em arquivos
5. **Visualização de resultados** estruturada
6. **Fluxo de dados** end-to-end

## 📈 Casos de Uso

### 1. Análise de Suporte

Identificar os problemas mais comuns relatados pelos usuários e buscar soluções externas.

### 2. Base de Conhecimento

Criar uma base de conhecimento enriquecida com artigos externos sobre tópicos frequentes.

### 3. Treinamento de Equipe

Fornecer material de referência para a equipe de suporte sobre os problemas mais comuns.

### 4. Documentação Automática

Gerar documentação automaticamente baseada em problemas reais dos usuários.

## ⚙️ Personalização

### Adicionar Novos Tópicos

Edite `topic_analyzer.py`:

```python
keywords_map = {
    "seu_topico": ["palavra1", "palavra2", "palavra3"],
    # ...
}
```

### Customizar Queries de Busca

Edite `external_search.py`:

```python
query_map = {
    "seu_topico": "sua query otimizada para busca",
    # ...
}
```

### Alterar Número de Artigos

```python
# No main.py
enriched_data = enrich_topics_with_external_articles(
    topics_list, 
    articles_per_topic=5  # Altere aqui
)
```

## 🔧 Troubleshooting

**Erro: "EXA_API_KEY não configurada"**
- Configure a chave no arquivo .env

**Erro: "Connection refused"**
- Verifique se o banco PostgreSQL está rodando

**Nenhum tópico encontrado**
- Verifique se há dados nas tabelas conversations e feedbacks

**Poucos artigos encontrados**
- Aumente o `num_results` na busca
- Ajuste as queries no `query_map`

## ✅ Conclusão

Sistema completo de enriquecimento de dados implementado com sucesso! O sistema:

- ✅ Analisa dados internos automaticamente
- ✅ Identifica padrões e tópicos frequentes
- ✅ Busca conhecimento externo relevante
- ✅ Organiza e persiste os resultados
- ✅ Fornece visualização clara dos dados

Pronto para uso em produção! 🚀
