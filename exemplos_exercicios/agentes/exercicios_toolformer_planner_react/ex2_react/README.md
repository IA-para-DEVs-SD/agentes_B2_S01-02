# Exercício 2 - ReAct (Reasoning + Acting)

## Objetivo

Implementar um agente que usa o padrão ReAct para analisar tickets de suporte.

## O que é ReAct?

ReAct é um padrão de agentes que combina:
- **Reasoning (Raciocínio)**: O agente pensa sobre o que fazer
- **Acting (Ação)**: O agente executa tools para obter informações
- **Observation (Observação)**: O agente analisa os resultados
- **Answer (Resposta)**: O agente fornece uma resposta estruturada

## Fluxo do Agente

```
1. THOUGHT → "Preciso buscar dados do ticket"
2. ACTION → Usa tool get_ticket_conversation
3. OBSERVATION → Analisa os dados retornados
4. ANSWER → Fornece resposta estruturada
```

## Funcionalidades

O agente recebe um ticket_id e retorna:
- Status atual do ticket
- Última mensagem do cliente
- Próximo passo sugerido

## Arquivos

- `tools.py`: Tool para buscar conversas de tickets
- `react_agent.py`: Implementação do agente ReAct
- `README.md`: Esta documentação

## Como Executar

```bash
# Certifique-se de que o PostgreSQL está rodando
wsl docker-compose up -d postgres

# Execute o agente
python react_agent.py
```

## Exemplos de Uso

### Entrada
```
"Analise o ticket 1007"
```

### Saída Esperada
```
Status: pending
Última mensagem do cliente: Pagamento recusado sem motivo
Próximo passo: Verificar com o cliente se o limite do cartão está disponível e se os dados estão corretos
```

## Diferença entre Toolformer e ReAct

### Toolformer (Ex1)
- Decide SE deve usar uma tool
- Foco: seleção de tools

### ReAct (Ex2)
- Sempre usa a tool quando necessário
- Foco: raciocínio + ação + análise
- Fornece respostas estruturadas e contextualizadas

## Testes Incluídos

1. Análise de ticket existente (1007)
2. Análise de outro ticket (1002)
3. Análise de ticket não encontrado (9999)
