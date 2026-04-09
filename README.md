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

[WIP]

## ⚙️ Setup

### 1. Create virtual environment

```bash
python -m venv .venv
```

Activate:

**Mac/Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

---

### 2. Install dependencies


```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
SUMMARY_MAX_POINTS=4
SUMMARY_SENTIMENT=true
SUMMARY_PRIORITY_RULES=true
```

These variables control the behavior of the summarization logic.



## ▶️ Run manually

```bash
python summarize.py
```

This will generate/update:

```
summary.json
```

📘 Setup do Banco + Dados (Mac / Linux / Windows)
Objetivo

Subir um banco PostgreSQL com Docker e carregar dados de tickets para uso com agentes de IA.

Pré-requisitos

Você precisa ter:

Docker instalado
Python 3.9+
pip
(opcional) virtualenv / venv
🐳 1. Instalar Docker
🍎 Mac

👉 Baixar:
https://www.docker.com/products/docker-desktop/

Passos:

Baixar Docker Desktop
Instalar e abrir
Aguardar mensagem: Docker is running

🐧 Linux (Ubuntu)
sudo apt update
sudo apt install docker.io -y

Iniciar serviço:

sudo systemctl start docker
sudo systemctl enable docker

Permitir rodar sem sudo:

sudo usermod -aG docker $USER

👉 depois disso, reinicia o terminal

🪟 Windows

👉 Baixar:
https://www.docker.com/products/docker-desktop/

Requisitos:

WSL2 ativado

Passos:

Instalar Docker Desktop
Ativar WSL2 se necessário
Abrir Docker Desktop
Verificar se está rodando
✅ 2. Validar Docker
docker --version
docker compose version

Se aparecer versão → OK

📁 3. Arquivos
[WIP]
⚙️ 4. Configurar docker-compose.yml

⚠️ IMPORTANTE: não usar version

🚀 5. Subir o banco
docker compose up -d

🔍 6. Verificar se rodou
docker ps

Você deve ver:

agentes_postgres   postgres:16   Up ...
🧪 7. Acessar o banco
docker exec -it agentes_postgres psql -U admin -d suporte_ai

📊 8. Verificar tabelas
Dentro do psql:

\dt

Você deve ver:

conversations
agent_configs
agent_runs

🐍 9. Criar ambiente Python
Mac / Linux
python3 -m venv .venv
source .venv/bin/activate
Windows
python -m venv .venv
.venv\Scripts\activate
📦 10. Instalar dependências
pip install -r requirements.txt


📥 11. Carregar dados
python load_data.py ou python3 load_data.py

✅ 12. Validar dados

Volte no psql:

SELECT COUNT(*) FROM conversations;

Se aparecer número > 0 → sucesso 🎉

🔥 Problemas comuns (e soluções)
❌ Erro: Docker não conecta

👉 solução:

abrir Docker Desktop
verificar se está rodando
❌ Erro: porta 5432 ocupada

👉 solução:
editar no compose:

ports:
  - "5433:5432"
❌ Erro: tabela não existe

👉 provável:
init.sql não rodou

👉 solução:

docker compose down -v
docker compose up -d
❌ Erro ao puxar imagem (EOF)

👉 solução:

docker pull postgres:16

ou trocar rede / desligar VPN


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