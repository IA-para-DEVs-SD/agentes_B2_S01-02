# 🐘 PostgreSQL com Docker Compose

Configuração simples e pronta para uso do PostgreSQL com Docker Compose, incluindo PgAdmin para gerenciamento visual.

---

## 📋 O que está incluído?

- **PostgreSQL 16 com pgvector** - Banco de dados relacional + suporte a embeddings para RAG
- **PgAdmin 4** - Interface web para gerenciar o PostgreSQL
- **Script de inicialização** - Cria tabelas e dados de exemplo automaticamente
- **Tabela de documentos com embeddings** - Pronta para usar em sistemas RAG
- **Função de busca vetorial** - `match_documents()` para similarity search

---

## 🚀 Como usar

### 🎯 Escolha sua ferramenta preferida

Você pode interagir com o PostgreSQL de várias formas:

| Ferramenta | Nível | Prós | Contras |
|------------|-------|------|---------|
| **Terminal (psql)** | Intermediário | ✅ Rápido<br>✅ Scriptável<br>✅ Sempre disponível | ❌ Menos visual<br>❌ Curva de aprendizado |
| **DBeaver** 🌟 | Iniciante | ✅ Interface visual<br>✅ Gratuito<br>✅ Autocomplete<br>✅ Multiplataforma | ❌ Precisa instalar |
| **PgAdmin** | Intermediário | ✅ Oficial PostgreSQL<br>✅ Já incluído no Docker | ❌ Interface menos amigável |
| **DataGrip** | Intermediário | ✅ Muito poderoso<br>✅ Integração IDE | ❌ Pago (JetBrains) |
| **Python/código** | Avançado | ✅ Automação<br>✅ Integração apps | ❌ Requer código |

**💡 Recomendação**: Se você está começando, use o **DBeaver** para visualizar e o **terminal** para queries rápidas!

---

### 1. Subir os containers

No diretório `modulo2_semana1`, execute:

```bash
docker-compose up -d
```

### 2. Verificar se os containers estão rodando

```bash
docker-compose ps
```

### 3. Acessar os serviços

#### PostgreSQL
- **Host**: `localhost`
- **Porta**: `5432`
- **Usuário**: `postgres`
- **Senha**: `postgres123`
- **Database**: `mydb`

**String de conexão:**
```
postgresql://postgres:postgres123@localhost:5432/mydb
```

#### PgAdmin (Interface Web)
- **URL**: http://localhost:5050
- **Email**: `admin@admin.com`
- **Senha**: `admin123`

---

## 🔌 Conectar ao PostgreSQL

### Opção 1: Via Terminal (psql) - Linha de comando

#### Entrar no console PostgreSQL interativo:

```bash
docker exec -it postgres_db psql -U postgres -d mydb
```

#### Executar queries diretas no terminal:

```bash
# Listar tabelas
docker exec postgres_db psql -U postgres -d mydb -c "\dt"

# Ver usuários
docker exec postgres_db psql -U postgres -d mydb -c "SELECT * FROM usuarios;"

# Ver produtos
docker exec postgres_db psql -U postgres -d mydb -c "SELECT * FROM produtos;"

# Contar registros
docker exec postgres_db psql -U postgres -d mydb -c "SELECT COUNT(*) FROM usuarios;"
```

#### Comandos úteis dentro do psql (após conectar):

```sql
-- Listar todas as tabelas
\dt

-- Descrever estrutura de uma tabela
\d usuarios

-- Listar todos os bancos de dados
\l

-- Sair do psql
\q

-- Ver todos os comandos disponíveis
\?
```

### Opção 2: DBeaver (Recomendado para Iniciantes!) 🌟

**DBeaver** é uma ferramenta visual **gratuita** e **open-source** para gerenciar bancos de dados.

#### Como instalar:

**macOS:**
```bash
brew install --cask dbeaver-community
```

**Windows:**
- Baixe em: https://dbeaver.io/download/
- Execute o instalador `.exe`

**Linux:**
```bash
# Ubuntu/Debian
sudo snap install dbeaver-ce

# ou baixe o .deb em https://dbeaver.io/download/
```

#### Como conectar no DBeaver:

1. Abra o DBeaver
2. Clique em **Database** → **New Database Connection**
3. Selecione **PostgreSQL**
4. Preencha os dados:
   - **Host**: `localhost`
   - **Port**: `5432`
   - **Database**: `mydb`
   - **Username**: `postgres`
   - **Password**: `postgres123`
5. Clique em **Test Connection** (vai baixar os drivers automaticamente na primeira vez)
6. Clique em **Finish**

Pronto! Agora você pode:
- ✅ Ver todas as tabelas visualmente
- ✅ Executar queries com autocomplete
- ✅ Ver dados em formato de tabela
- ✅ Exportar dados para CSV/Excel
- ✅ Criar diagramas ER

### Opção 3: DataGrip (JetBrains - Pago)

Se você já usa IntelliJ/PyCharm, pode usar o **DataGrip**:

1. File → New → Data Source → PostgreSQL
2. Host: `localhost`, Port: `5432`
3. Database: `mydb`
4. User: `postgres`, Password: `postgres123`

### Opção 4: Via Python

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="postgres123"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM usuarios;")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
```

### Opção 5: Usar o PgAdmin (já incluído no Docker Compose)

Acesse http://localhost:5050 e siga as instruções na seção "Configurar PgAdmin" abaixo.

---

## 🔧 Configurar PgAdmin

1. Acesse http://localhost:5050
2. Login com `admin@admin.com` / `admin123`
3. Clique em **Add New Server**
4. Na aba **General**:
   - Name: `Local PostgreSQL`
5. Na aba **Connection**:
   - Host: `postgres` (nome do service no docker-compose)
   - Port: `5432`
   - Database: `mydb`
   - Username: `postgres`
   - Password: `postgres123`
6. Clique em **Save**

---

## 📊 Tabelas criadas automaticamente

### Tabela `usuarios`
```sql
SELECT * FROM usuarios;
```

| id | nome | email | data_criacao |
|----|------|-------|--------------|
| 1 | João Silva | joao@email.com | ... |
| 2 | Maria Santos | maria@email.com | ... |
| 3 | Pedro Oliveira | pedro@email.com | ... |

### Tabela `produtos`
```sql
SELECT * FROM produtos;
```

| id | nome | descricao | preco | estoque | data_criacao |
|----|------|-----------|-------|---------|--------------|
| 1 | Notebook | Notebook Dell i5... | 3500.00 | 10 | ... |
| 2 | Mouse | Mouse sem fio... | 150.00 | 50 | ... |
| 3 | Teclado | Teclado mecânico... | 450.00 | 25 | ... |

---

## 💻 Exemplos de Queries via Terminal

### Queries básicas (executar direto no terminal sem entrar no psql):

```bash
# 1. Ver todos os usuários
docker exec postgres_db psql -U postgres -d mydb -c "SELECT * FROM usuarios;"

# 2. Ver todos os produtos
docker exec postgres_db psql -U postgres -d mydb -c "SELECT * FROM produtos;"

# 3. Buscar produto específico
docker exec postgres_db psql -U postgres -d mydb -c "SELECT * FROM produtos WHERE nome = 'Mouse';"

# 4. Produtos com preço maior que 200
docker exec postgres_db psql -U postgres -d mydb -c "SELECT nome, preco FROM produtos WHERE preco > 200;"

# 5. Contar quantos produtos existem
docker exec postgres_db psql -U postgres -d mydb -c "SELECT COUNT(*) as total FROM produtos;"

# 6. Somar valor total do estoque
docker exec postgres_db psql -U postgres -d mydb -c "SELECT SUM(preco * estoque) as valor_total FROM produtos;"

# 7. Inserir novo usuário
docker exec postgres_db psql -U postgres -d mydb -c "INSERT INTO usuarios (nome, email) VALUES ('Ana Costa', 'ana@email.com');"

# 8. Atualizar estoque de um produto
docker exec postgres_db psql -U postgres -d mydb -c "UPDATE produtos SET estoque = 30 WHERE nome = 'Mouse';"

# 9. Deletar um usuário
docker exec postgres_db psql -U postgres -d mydb -c "DELETE FROM usuarios WHERE email = 'ana@email.com';"

# 10. Ordenar produtos por preço
docker exec postgres_db psql -U postgres -d mydb -c "SELECT nome, preco FROM produtos ORDER BY preco DESC;"
```

### Modo interativo (entrar no psql e executar múltiplas queries):

```bash
# Entrar no console PostgreSQL
docker exec -it postgres_db psql -U postgres -d mydb
```

Agora você está dentro do `psql`. Execute queries diretamente:

```sql
-- Listar todas as tabelas
\dt

-- Ver estrutura da tabela usuarios
\d usuarios

-- Buscar usuários
SELECT * FROM usuarios;

-- Buscar produtos com estoque baixo
SELECT nome, estoque FROM produtos WHERE estoque < 20;

-- Criar nova tabela
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    produto_id INTEGER REFERENCES produtos(id),
    quantidade INTEGER NOT NULL,
    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir pedido
INSERT INTO pedidos (usuario_id, produto_id, quantidade) VALUES (1, 2, 3);

-- Join entre tabelas
SELECT 
    u.nome as usuario, 
    p.nome as produto, 
    ped.quantidade,
    ped.data_pedido
FROM pedidos ped
JOIN usuarios u ON ped.usuario_id = u.id
JOIN produtos p ON ped.produto_id = p.id;

-- Sair do psql
\q
```

---

## 🛠️ Comandos úteis

### Parar os containers
```bash
docker-compose stop
```

### Iniciar containers parados
```bash
docker-compose start
```

### Parar e remover containers
```bash
docker-compose down
```

### Parar e remover containers + volumes (⚠️ apaga os dados!)
```bash
docker-compose down -v
```

### Ver logs do PostgreSQL
```bash
docker-compose logs postgres
```

### Ver logs do PgAdmin
```bash
docker-compose logs pgadmin
```

### Seguir logs em tempo real
```bash
docker-compose logs -f postgres
```

---

## 📝 Executar scripts SQL

### Método 1: Via arquivo
```bash
docker exec -i postgres_db psql -U postgres -d mydb < seu_script.sql
```

### Método 2: Via comando direto
```bash
docker exec postgres_db psql -U postgres -d mydb -c "SELECT * FROM usuarios;"
```

### Método 3: Copiar arquivo para dentro do container
```bash
docker cp seu_script.sql postgres_db:/tmp/
docker exec postgres_db psql -U postgres -d mydb -f /tmp/seu_script.sql
```

---

## 🔐 Alterar senhas (opcional)

Edite o arquivo `docker-compose.yml`:

```yaml
environment:
  POSTGRES_PASSWORD: sua_senha_forte_aqui  # ← altere aqui
```

Depois recrie os containers:
```bash
docker-compose down -v
docker-compose up -d
```

---

## 🗂️ Persistência de dados

Os dados do PostgreSQL são armazenados em um **volume Docker** chamado `postgres_data`. Isso significa que:

- ✅ Os dados persistem mesmo após `docker-compose down`
- ✅ Você pode parar e iniciar os containers sem perder dados
- ⚠️ Use `docker-compose down -v` **apenas** se quiser apagar todos os dados

---

## 🐛 Troubleshooting

### Porta 5432 já está em uso
Se você já tem PostgreSQL instalado localmente:

**Opção 1**: Pare o PostgreSQL local
```bash
# macOS
brew services stop postgresql

# Linux
sudo systemctl stop postgresql
```

**Opção 2**: Altere a porta no docker-compose.yml
```yaml
ports:
  - "5433:5432"  # ← use porta 5433 no host
```

### Container não inicia
Verifique os logs:
```bash
docker-compose logs postgres
```

### Resetar tudo do zero
```bash
docker-compose down -v
docker volume rm modulo2_semana1_postgres_data
docker-compose up -d
```

---

## 📚 Recursos adicionais

- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [PgAdmin Docs](https://www.pgadmin.org/docs/)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

## 🎯 Próximos passos

1. ✅ Subir os containers
2. ✅ Conectar via PgAdmin ou DBeaver
3. ✅ Testar as queries nas tabelas de exemplo
4. 🚀 Começar a desenvolver!

---

## 🤖 Usar PostgreSQL para RAG (Retrieval-Augmented Generation)

### O que é RAG?

RAG combina **busca semântica** com **LLMs**:
1. Documentos são convertidos em **embeddings** (vetores)
2. Query do usuário também vira embedding
3. Busca por **similaridade vetorial** encontra documentos relevantes
4. LLM usa esses documentos como **contexto** para responder

### Por que PostgreSQL para RAG?

✅ **pgvector** - Extensão para armazenar e buscar vetores  
✅ **ACID** - Transações confiáveis  
✅ **Gratuito e open-source**  
✅ **Escalável** - Suporta milhões de vetores  
✅ **SQL familiar** - Usa SQL normal + operadores vetoriais  

### Tabela já criada para RAG

```sql
-- Ver documentos
SELECT * FROM documents_summary;

-- Buscar por conteúdo
SELECT content, metadata FROM documents WHERE content LIKE '%PostgreSQL%';

-- Ver documentos com embeddings
SELECT id, content, has_embedding FROM documents_summary;
```

### Exemplo completo de RAG com Python

Veja o arquivo `exemplo_rag_postgres.py` que mostra:

1. **Como gerar embeddings** com OpenAI
2. **Como armazenar** documentos com embeddings
3. **Como fazer busca por similaridade**
4. **Como usar com LLM** (RAG completo)

#### Instalar dependências:

```bash
pip install psycopg2-binary openai python-dotenv
```

#### Configurar .env:

```bash
echo "OPENAI_API_KEY=sua_chave_aqui" > .env
```

#### Executar exemplo:

```bash
python exemplo_rag_postgres.py
```

### Operadores vetoriais do pgvector

```sql
-- Distância L2 (Euclidiana)
SELECT embedding <-> '[1,2,3]'::vector FROM documents;

-- Similaridade de coseno (recomendado para embeddings)
SELECT embedding <=> '[1,2,3]'::vector FROM documents;

-- Produto interno
SELECT embedding <#> '[1,2,3]'::vector FROM documents;
```

### Função de busca por similaridade

```sql
-- Buscar os 3 documentos mais similares
SELECT * FROM match_documents(
    '[1.2, 0.5, ..., 0.8]'::vector(1536),  -- embedding da query
    3,                                       -- quantos resultados
    '{}'::jsonb                              -- filtros opcionais
);

-- Com filtro por categoria
SELECT * FROM match_documents(
    '[1.2, 0.5, ..., 0.8]'::vector(1536),
    5,
    '{"category": "ai"}'::jsonb
);
```

### Workflow RAG típico

```python
# 1. Usuário faz pergunta
user_query = "Como usar Docker?"

# 2. Gerar embedding da pergunta
query_embedding = get_embedding(user_query)

# 3. Buscar documentos similares no PostgreSQL
cursor.execute(
    "SELECT * FROM match_documents(%s::vector, 5)",
    (query_embedding,)
)
docs = cursor.fetchall()

# 4. Montar contexto
context = "\n".join([doc[1] for doc in docs])

# 5. Chamar LLM com contexto
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Use apenas o contexto fornecido"},
        {"role": "user", "content": f"Contexto: {context}\n\nPergunta: {user_query}"}
    ]
)
```

### Dicas de Performance

1. **Índice IVFFlat** - Já criado automaticamente para busca rápida
2. **Normalizar embeddings** - Melhora a busca por similaridade de coseno
3. **Chunk size** - 500-1000 tokens por documento é ideal
4. **Batch inserts** - Insira múltiplos documentos de uma vez

### Comparação com outras soluções

| Solução | Prós | Contras |
|---------|------|---------|
| **PostgreSQL + pgvector** | ✅ Gratuito<br>✅ ACID<br>✅ SQL familiar | ❌ Menos features que dedicados |
| **Pinecone** | ✅ Muito rápido<br>✅ Gerenciado | ❌ Pago<br>❌ Vendor lock-in |
| **Qdrant** | ✅ Open-source<br>✅ Rápido | ❌ Mais complexo de setup |
| **Supabase** | ✅ PostgreSQL managed<br>✅ UI | ❌ Limitações free tier |
| **ChromaDB** | ✅ Simples<br>✅ Python-first | ❌ Menos robusto |

### Recursos adicionais sobre RAG

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [LangChain + PostgreSQL](https://python.langchain.com/docs/integrations/vectorstores/pgvector)
