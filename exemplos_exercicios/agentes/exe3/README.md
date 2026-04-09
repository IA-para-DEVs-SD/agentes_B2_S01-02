# Proposta do exercício
## Exercício — Análise de Feedbacks e Geração de Relatório
A empresa tem uma tabela com feedbacks de usuários.

O objetivo é construir um processo que analise cada feedback individualmente e, ao final, gere um relatório (números consolidados e relatório para a gerência) para o negócio.

O que os alunos devem fazer:

a) Ler os feedbacks de uma tabela no banco
b) Analisar cada feedback com apoio de LLM
c) Classificar cada feedback
d) Salvar os resultados estruturados
e) Gerar um relatório final com os principais achados

Tabela de entrada: feedbacks 

Exemplos de conteúdo:
1 | O app trava quando tento abrir a tela de pagamento
2 | Gostei muito da nova interface
3 | O sistema está muito lento
4 | Não consegui finalizar minha compra
5 | Atendimento excelente
Saída esperada por feedback
Para cada feedback, o agente pode gerar algo assim:
{
 "feedback_id": 1,
 "categoria": "bug",
 "sentimento": "negativo",
 "resumo": "Usuário relatou falha ao acessar a tela de pagamento."
}

Categorias sugeridas
Você pode deixar simples:
bug
elogio
pagamento
performance
atendimento
outros

### Relatório consolidado 

Depois de processar todos os feedbacks, gerar um relatório como:
Nota: números fictícios, não é um gabarito
{
 "total_feedbacks": 5,
 "categorias": {
   "bug": 1,
   "elogio": 2,
   "pagamento": 1,
   "performance": 1
 },
 "sentimentos": {
   "positivo": 2,
   "negativo": 3,
   "neutro": 0
 },
 "principais_pontos": [
   "Usuários relataram problemas técnicos no app",
   "Houve elogios à nova interface e ao atendimento",
   "Questões de pagamento e lentidão apareceram com frequência"
 ]
}

# Relatório em texto
Para simular o que alguém entregaria para liderança, produto ou suporte.


# Como resolver: 
Estrutura do exercício
Parte 1 — análise individual
Criar uma função ou agente que receba um feedback e devolva:
1. categoria
2. sentimento
3. resumo

Parte 2 — processamento em lote
Ler todos os feedbacks da tabela e aplicar a análise para cada linha.

Parte 3 — geração de relatório
Consolidar os resultados e responder perguntas como:
1. quantos feedbacks havia
2. quais categorias apareceram mais
3. qual sentimento predominou
5. quais temas principais surgiram

O que isso ensina
camada 1: micro
analisar corretamente cada texto
camada 2: macro
transformar várias análises em visão de negócio
