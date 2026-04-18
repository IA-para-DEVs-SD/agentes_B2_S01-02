# Exercício 7 - Busca Externa com Exa AI

## 📌 Visão Geral

Este exercício demonstra como integrar uma ferramenta de busca externa (Exa AI) para permitir que agentes acessem informações atualizadas da web, complementando dados internos do banco de dados.

## ✅ Status da Implementação

- ✅ Biblioteca exa-py instalada
- ✅ Funções de busca implementadas
- ✅ Script de teste criado
- ✅ Script de demonstração criado
- ⚠️  Requer configuração da chave API

## 🎯 O que é o Exa?

Exa é uma API de busca semântica que permite:
- 🌐 Buscar informações atualizadas na web
- 📊 Complementar dados internos do banco
- ❓ Responder perguntas que não estão no sistema
- 🔍 Usar busca semântica (não apenas keywords)

## 📁 Arquivos do Projeto

```
exe7/
├── tools_external.py    # Implementação das funções de busca
├── test_exa.py         # Script de teste original
├── demo_exa.py         # Script de demonstração
├── README.MD           # Documentação original
└── INSTRUCOES.md       # Este arquivo
```

## 🔧 Configuração

### 1. Obter Chave da API

1. Acesse: https://exa.ai/
2. Crie uma conta gratuita
3. Obtenha sua API key no dashboard
4. Adicione no arquivo `.env` na raiz do projeto:

```env
EXA_API_KEY='sua-chave-aqui'
```

### 2. Instalar Dependências

A biblioteca já foi instalada, mas se necessário:

```bash
pip install exa-py
```

## 🚀 Como Usar

### Executar Demonstração

```bash
python exemplos_exercicios/agentes/exe7/demo_exa.py
```

Este script:
- Verifica se a chave está configurada
- Mostra instruções se não estiver
- Executa 2 buscas de exemplo se estiver configurada

### Executar Teste Original

```bash
python exemplos_exercicios/agentes/exe7/test_exa.py
```

## 📚 Funções Disponíveis

### 1. `search_external(query, num_results=5)`

Busca informações externas usando Exa AI.

**Parâmetros:**
- `query` (str): Consulta de busca
- `num_results` (int): Número de resultados (padrão: 5)

**Retorna:**
```python
[
    {
        "source": "external",
        "title": "Título do resultado",
        "text": "Texto do conteúdo (primeiros 500 chars)",
        "url": "https://..."
    }
]
```

**Exemplo:**
```python
from tools_external import search_external

results = search_external("login issues password reset", num_results=3)
for r in results:
    print(f"{r['title']} - {r['url']}")
```

### 2. `filter_external_results(results, keyword)`

Filtra resultados por palavra-chave.

**Exemplo:**
```python
filtered = filter_external_results(results, "password")
```

### 3. `summarize_external_results(results)`

Cria um resumo formatado dos resultados.

**Exemplo:**
```python
summary = summarize_external_results(results)
print(summary)
```

## 💡 Casos de Uso

### 1. Buscar Soluções Técnicas

```python
results = search_external("login issues password reset")
```

Útil quando o banco interno não tem informações sobre um problema específico.

### 2. Pesquisar Problemas de Pagamento

```python
results = search_external("problemas com pagamento online")
```

Complementa dados internos com soluções da web.

### 3. Encontrar Guias e Tutoriais

```python
results = search_external("how to troubleshoot app crashes")
```

Busca documentação e guias externos.

## 🔄 Integração com Agentes

A função `search_external` pode ser usada como uma tool em agentes:

```python
from tools_external import search_external

# Em um agente com tool calling
def handle_external_search(query: str):
    results = search_external(query, num_results=3)
    
    if not results:
        return "Nenhum resultado encontrado."
    
    response = "Encontrei as seguintes informações:\n\n"
    for i, r in enumerate(results, 1):
        response += f"{i}. {r['title']}\n"
        response += f"   {r['text'][:100]}...\n"
        response += f"   Fonte: {r['url']}\n\n"
    
    return response
```

## 📊 Exemplo de Saída

```
============================================================
TESTE 1: Busca sobre problemas de login
============================================================

📊 Resultados encontrados: 3

1. How to Reset Your Password - Complete Guide
   URL: https://example.com/password-reset
   Preview: Learn how to reset your password in 3 easy steps. First, click on the forgot password link...

2. Troubleshooting Login Issues
   URL: https://example.com/login-troubleshooting
   Preview: Common login problems and their solutions. Check your internet connection, clear cache...

3. Account Recovery Best Practices
   URL: https://example.com/account-recovery
   Preview: Secure methods for recovering your account access. Use two-factor authentication...
```

## ⚠️ Limitações

- **Requer chave API**: Necessário criar conta no Exa
- **Limites de uso**: Plano gratuito tem limites de requisições
- **Latência**: Buscas externas são mais lentas que consultas ao banco
- **Custo**: Pode ter custos dependendo do volume de uso

## 🎓 Conceitos Aplicados

1. **Integração com APIs externas**
2. **Busca semântica** (não apenas keywords)
3. **Complementação de dados** internos com externos
4. **Tratamento de resultados** de APIs
5. **Formatação e resumo** de informações

## 🔐 Segurança

- ✅ Chave API armazenada em variável de ambiente
- ✅ Não expor a chave no código
- ✅ Limitar tamanho dos resultados (500 chars)
- ✅ Validar entrada antes de buscar

## 📈 Próximos Passos

1. Configure sua chave EXA_API_KEY
2. Execute o demo para testar
3. Integre com seus agentes existentes
4. Experimente diferentes tipos de consultas
5. Combine resultados externos com dados internos

## 🆘 Troubleshooting

**Erro: "EXA_API_KEY não definida"**
- Verifique se adicionou a chave no arquivo .env
- Certifique-se de que o arquivo .env está na raiz do projeto

**Erro: "Invalid API key"**
- Verifique se a chave está correta
- Confirme que a conta Exa está ativa

**Erro: "Rate limit exceeded"**
- Você atingiu o limite de requisições
- Aguarde ou faça upgrade do plano

## ✅ Conclusão

O exercício 7 demonstra como expandir as capacidades de um agente com busca externa, permitindo acesso a informações atualizadas da web quando os dados internos não são suficientes!
