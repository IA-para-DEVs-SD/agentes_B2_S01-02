RAG com N8N + Supabase 
Pipeline completo de Retrieval-Augmented Generation: PDF/texto → chunks → embeddings → pgvector → busca semântica → LLM.

Stack
ServiçoFunçãoURLN8N CloudOrquestrador dos fluxoshttps://n8n.ioSupabasePostgreSQL + pgvector (vector store)https://supabase.comOpenAIEmbeddings + LLM (GPT-4o)https://platform.openai.com

Arquitetura
INGESTION (uma vez — popula o banco)
Texto/PDF → Default Data Loader → Text Splitter → OpenAI Embeddings → Supabase Vector Store

INFERENCE (cada pergunta)
Chat Trigger → AI Agent → Supabase Vector Store Tool → OpenAI Chat Model → Resposta

1. Setup Supabase
1.1 Criar conta e projeto

Acessar https://supabase.com → Start your project
Login com GitHub
New Project → Name: rag-n8n → Region: South America (São Paulo)
Definir senha do banco — anotar essa senha!
Aguardar ~2 minutos para provisionar

1.2 Pegar credenciais
Connection String (para credencial Postgres no N8N):

No painel → clicar em Connect no topo
Ir em Connection string → URI
Substituir [YOUR-PASSWORD] pela senha criada:

postgresql://postgres:SUA_SENHA@db.SEU_PROJETO.supabase.co:5432/postgres
Service Role Key (para credencial Supabase API no N8N):

Settings → API
Project API keys → service_role → Reveal
Copiar — nunca expor no frontend!

1.3 SQL: Ativar pgvector
Rodar no SQL Editor do Supabase:
sqlcreate extension if not exists vector;
1.4 SQL: Criar tabela de documentos
sqlcreate table documents (
  id        bigserial primary key,
  content   text,           -- texto do chunk
  metadata  jsonb,          -- fonte, página, etc.
  embedding vector(1536)    -- vetor OpenAI ada-002 / text-embedding-3-small
);
1.5 SQL: Criar índice de busca
sqlcreate index on documents
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

Por que vector(1536)?
O modelo text-embedding-3-small da OpenAI gera vetores de 1536 dimensões.
O índice ivfflat acelera a busca por similaridade coseno — obrigatório para boa performance.

1.6 SQL: Criar função match_documents ⚠️ obrigatória
Sem essa função o N8N retorna erro PGRST202. Rodar antes de testar o fluxo de Inference:
sqlcreate or replace function match_documents (
  query_embedding vector(1536),
  match_count     int   default 5,
  filter          jsonb default '{}'
)
returns table (
  id         bigint,
  content    text,
  metadata   jsonb,
  similarity float
)
language plpgsql as $$
begin
  return query
  select
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where documents.metadata @> filter
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;

O que essa função faz?
É uma abstração do similarity search. O N8N chama match_documents(embedding, 5) via PostgREST
e ela executa a busca vetorial por similaridade coseno (<=>) retornando os chunks mais relevantes.
O campo similarity vai de 0 (oposto) a 1.0 (idêntico).


2. Setup N8N Cloud
2.1 Criar conta

Acessar https://n8n.io → Get started for free
Trial gratuito de 14 dias — sem cartão

2.2 Criar credenciais
Em Settings → Credentials → New:
Credencial 1 — Postgres (para Connection String):

Type: Postgres
Host: db.SEU_PROJETO.supabase.co
Database: postgres
User: postgres
Password: sua senha do Supabase
Port: 5432
SSL: ativado

Credencial 2 — Supabase API (para Vector Store):

Type: Supabase API
Host: https://SEU_PROJETO.supabase.co
Service Role Secret: chave service_role do Supabase

Credencial 3 — OpenAI:

Type: OpenAI API
API Key: sua chave da OpenAI


3. Fluxo de Ingestion
Estrutura
Chat Trigger
  → Supabase Vector Store (Insert Documents)
      ├── Default Data Loader
      │     └── [Text Splitter — sub-nó]
      └── Embeddings OpenAI
Configurações dos nós
Supabase Vector Store:

Operation Mode: Insert Documents
Credential: Supabase API
Table Name: documents

Default Data Loader:

Type of Data: JSON
Mode: Load All Input Data
Text Splitting: Custom

Embeddings OpenAI:

Credential: OpenAI
Model: text-embedding-3-small

Testar
Abrir o chat do fluxo e colar um texto. Verificar no Supabase:
sqlselect id, content from documents limit 5;

4. Fluxo de Inference
Estrutura
Chat Trigger
  → AI Agent
      ├── OpenAI Chat Model (GPT-4o)
      ├── Simple Memory
      └── Supabase Vector Store Tool (Retrieve for AI Agent)
            └── Embeddings OpenAI
Configurações dos nós
AI Agent — System Prompt:
Você é um assistente especialista no documento carregado.
Sempre use a tool de busca para encontrar informações relevantes
antes de responder. Base suas respostas APENAS no conteúdo
encontrado. Se não encontrar a informação, diga que não está
no documento.
OpenAI Chat Model:

Credential: OpenAI
Model: gpt-4o

Supabase Vector Store Tool:

Operation Mode: Retrieve Documents (As Tool for AI Agent)
Credential: Supabase API
Table Name: documents
Description: Busca informações relevantes nos documentos. Use sempre que precisar responder perguntas sobre o conteúdo carregado.
Limit: 5

Embeddings OpenAI (sub-nó do Vector Store Tool):

Model: text-embedding-3-small


5. SQL: Queries úteis
sql-- Ver chunks salvos
select id, content, metadata from documents limit 5;

-- Contar total de chunks
select count(*) from documents;

-- Ver os embeddings (vetores numéricos)
select id, content, embedding from documents limit 1;

-- Ver metadados de cada chunk
select id, metadata->>'source' as fonte, length(content) as tamanho
from documents order by id;

-- Limpar todos os dados (cuidado!)
truncate table documents;

6. Exportar/Importar workflows no N8N
Exportar: Abrir fluxo → "..." (três pontinhos) → Download
Importar: Novo workflow → "..." → Import from file
Os arquivos exportados contêm todos os nós e conexões — sem as credenciais por segurança.

7. Dicas para a aula

Use um PDF de documentação técnica real — manual do N8N, spec da OpenAI, etc.
O verbose do AI Agent mostra quais chunks foram recuperados — ótimo para explicar o RAG
Chunk size 500 / overlap 50 é um bom ponto de partida
A função match_documents é obrigatória — criar ANTES de testar o Inference
Exportar os dois workflows como JSON/YAML para os alunos importarem direto


Referências

N8N Docs: https://docs.n8n.io
Supabase pgvector: https://supabase.com/docs/guides/ai/vector-columns
OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings