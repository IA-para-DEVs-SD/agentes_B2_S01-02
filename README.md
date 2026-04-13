# 🤖 Customer Interaction Summarizer (Kiro Demo)

This project demonstrates the evolution from **Assistant → Workflow → Agent**, using a simple and realistic use case: summarizing customer interactions.

---

## 🎯 Objective

Automatically generate a structured summary (`summary.json`) from customer interactions (`interactions.txt`), using:

* Python script
* Environment variables (`.env`)
* Kiro hook for automation

---

## 🧱 Project Structure

```
.
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── init.sql
├── load_data.py
├── requirements.txt
├── .env (em exemplos_exercicios/)
├── exemplos_exercicios/
│   ├── .env
│   ├── exemplos/
│   ├── exercicio_1/
│   ├── exercicio_2/
│   └── agentes/
│       ├── exe1/   # Agente baseado em regras
│       ├── exe2/   # Agente com LLM e tool calling
│       └── exe3/   # Análise de feedbacks com Gemini
└── .kiro/
    ├── hooks/
    └── steering/
```

---

## ⚙️ Setup

### Pré-requisitos

- Docker e Docker Compose instalados
- Chaves de API configuradas no `.env` (Anthropic, OpenAI, Gemini)

---

### 🐳 Setup com Docker (recomendado)

Todo o ambiente (banco + app Python) roda em containers. Não precisa de venv, pip install, nem versão específica de Python na máquina.

#### 1. Subir tudo

```bash
docker compose up -d
```

Isso sobe:
- `agentes_postgres` — PostgreSQL 16 com banco `suporte_ai`
- `agentes_app` — Python 3.12 com todas as dependências instaladas

O serviço `app` só inicia quando o Postgres estiver pronto (healthcheck).

#### 2. Carregar dados no banco

```bash
docker compose exec app python load_data.py
```

#### 3. Rodar scripts

```bash
docker compose exec app python exemplos_exercicios/agentes/exe1/run_support_agent.py
```

#### 4. Shell interativo

```bash
docker compose exec app bash
```

Dentro do container, rode qualquer script normalmente.

#### 5. Parar tudo

```bash
docker compose down
```

Para remover também os dados do banco:

```bash
docker compose down -v
```

---

### 🐍 Setup local (alternativa sem Docker)

Se preferir rodar sem Docker, você precisa de Python 3.9+ e um PostgreSQL rodando na porta 5432.

#### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

**Mac/Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

#### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

#### 3. Subir apenas o banco via Docker

```bash
docker compose up -d postgres
```

#### 4. Carregar dados

```bash
python load_data.py
```

#### 5. Rodar scripts

```bash
python exemplos_exercicios/agentes/exe1/run_support_agent.py
```

---

## 🔐 Environment Variables

O arquivo `exemplos_exercicios/.env` deve conter:

```env
SUMMARY_MAX_POINTS=4
SUMMARY_SENTIMENT=true
SUMMARY_PRIORITY_RULES=true
ANTHROPIC_API_KEY=sua-chave-aqui
OPENAI_API_KEY=sua-chave-aqui
GEMINI_API_KEY=sua-chave-aqui
```

No setup Docker, o `env_file` do compose já carrega essas variáveis automaticamente no container.

---

## 📊 Verificar o banco

### Via Docker

```bash
docker exec -it agentes_postgres psql -U admin -d suporte_ai
```

Dentro do psql:

```sql
\dt
SELECT COUNT(*) FROM conversations;
SELECT COUNT(*) FROM feedbacks;
```

Tabelas esperadas: `conversations`, `agent_configs`, `agent_runs`, `feedbacks`

---

## 🔥 Problemas comuns

| Problema | Solução |
|---|---|
| Docker não conecta | Abrir Docker Desktop e verificar se está rodando |
| Porta 5432 ocupada | Alterar no compose: `"5433:5432"` |
| Tabela não existe | `docker compose down -v` e subir novamente |
| Erro ao puxar imagem | `docker pull postgres:16` ou desligar VPN |


# Agentes
Path: /agentes_B2_S01-02/exemplos_exercicios/agentes/
## exe1 - Para começarmos a entender
### 🎯 Objetivo pedagógico

Esse exercício tem como objetivo mostrar:

Como estruturar um fluxo básico de agente
Como organizar entrada → processamento → saída
As limitações de abordagens puramente determinísticas

Ele serve como base para comparação com versões mais avançadas, especialmente agentes com LLM, que conseguem lidar melhor com linguagem natural e ambiguidade.
O primeiro exercício consiste na construção de um agente de suporte simples, baseado em regras fixas e sem uso de modelos de linguagem.

### Funcionamento
Esse agente recebe o ID de um ticket, recupera a conversa associada e executa três tarefas principais:

a) Classifica a categoria do problema
b) Verifica se é necessário follow-up
c) Gera um resumo da conversa

A lógica utilizada é determinística, baseada em palavras-chave. Por exemplo, termos como “login”, “senha” ou “acesso” classificam o ticket como problema de login, enquanto palavras como “pagamento” ou “cartão” indicam questões financeiras.

⚙️ Características principais
Não utiliza IA ou LLM
Funciona com regras explícitas (if/else)
Totalmente previsível e controlável
Baixo custo computacional
Fácil de entender e debugar

⚠️ Limitações

Apesar de funcional, esse agente apresenta limitações importantes:

Depende de palavras exatas (não entende variações de linguagem)
Não captura contexto ou intenção
Difícil de escalar (regras crescem rapidamente)
Pode falhar facilmente em casos ambíguos

Para rodar, vá até a pasta e rode:
python3 run_support_agent.py <ticket_id> ou python run_support_agent.py <ticket_id>

🧠 Exercício 2 — Agente de Suporte com LLM e Tool Calling
## 🎯 Objetivo pedagógico

Este exercício mostra:

- Como construir agentes com LLM
- Como integrar ferramentas externas
- Como lidar com saída estruturada
- A importância de controle e validação em sistemas com IA

No segundo exercício, evoluímos o agente de suporte para utilizar um modelo de linguagem (LLM) com capacidade de tomar decisões e acionar ferramentas dinamicamente.

Em vez de seguir regras fixas, o agente passa a interpretar o contexto da conversa e decidir quais ações executar, como:

a) Buscar a conversa do ticket
b) Classificar a categoria
c) Identificar necessidade de follow-up
d) Gerar resumo

Isso é feito através de tool calling, onde o modelo escolhe quais funções utilizar durante a execução.

⚙️ Características principais
Utiliza LLM (ex: Gemini)
Capacidade de decisão dinâmica
Integração com ferramentas (functions/tools)
Suporte a saída estruturada (JSON)
Mais flexível e adaptável

🔄 Como funciona

O fluxo do agente passa a ser:

Usuário → LLM → decide qual tool chamar → executa tool → retorna resultado → LLM continua → resposta final

Ou seja, o LLM atua como um orquestrador inteligente, não apenas como gerador de texto.

### Melhorias em relação ao Exercício 1
Entende variações de linguagem natural
Não depende de palavras exatas
Mais robusto para casos reais
Reduz necessidade de regras manuais
Mais fácil de escalar para novos cenários


# Ferramenta para visualização dos dados

Além do LLM e das tools, o exercício inclui um banco PostgreSQL local. Nesse caso, o DBeaver entra como apoio para explorar os tickets, validar consultas e enxergar de forma concreta como o agente interage com dados reais.

💻 Como baixar e usar o DBeaver
🧭 O que é o DBeaver

O DBeaver é uma ferramenta para:

conectar em bancos de dados
visualizar tabelas
rodar queries SQL
explorar dados


⬇️ 1. Download
Acesse:
👉 https://dbeaver.io/download/
Escolha:
DBeaver Community (gratuito)
Baixe para seu sistema:
Mac (.dmg)
Windows (.exe)
Linux
⚙️ 2. Instalação
Mac
Abrir o .dmg
Arrastar para Applications
Windows
Next → Next → Install

👉 padrão, sem segredo

🚀 3. Abrir e criar conexão
Abrir o DBeaver
Clicar em:
👉 New Database Connection
Escolher:
👉 PostgreSQL
🔌 4. Conectar no banco (Docker)

Usando seu docker-compose, preenche assim:

Host: localhost
Port: 5432
Database: suporte_ai
Username: admin
Password: admin123

👉 Test Connection
👉 Finish

🧪 5. Ver os dados

Depois de conectar:

Expande:
database → schemas → public → tables

Você deve ver suas tabelas (ex: tickets)

👉 Clica com botão direito → View Data

💡 6. Rodar SQL (muito importante pra aula)

Clique com botão direito → SQL Editor

E roda:

SELECT * FROM conversations;

ou

SELECT * FROM agent_runs;

Qdrant - http://localhost:6333/dashboard#/console

Rodar o langfuse
chmod +x start_langfuse.sh
./start_langfuse.sh



Caso docker compose down e docker compose up -d não resolver
docker rm -f agentes_pgadmin agentes_postgres agentes_qdrant