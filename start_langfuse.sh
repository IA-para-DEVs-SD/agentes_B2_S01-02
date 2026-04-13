#!/bin/bash

echo "🚀 Setup completo do Langfuse..."

# =========================
# 1. Clonar repo
# =========================
if [ ! -d "langfuse" ]; then
  echo "📦 Clonando Langfuse..."
  git clone https://github.com/langfuse/langfuse.git
fi

cd langfuse || exit

# =========================
# 2. Criar .env
# =========================
if [ ! -f ".env" ]; then
  echo "⚙️ Criando .env..."

  cat <<EOL > .env
NEXTAUTH_SECRET=mysecret123
SALT=mysalt123

CLICKHOUSE_URL=http://clickhouse:8123
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
REDIS_URL=redis://redis:6379
EOL
fi

# =========3000================
# 3. Ajustar porta do Postgres (evitar conflito)
# =========================
echo "🔧 Ajustando porta do Postgres para 5433..."

# Mac (BSD sed)
sed -i '' 's/"5432:5432"/"5433:5432"/g' docker-compose.yml 2>/dev/null

# Linux fallback
sed -i 's/"5432:5432"/"5433:5432"/g' docker-compose.yml 2>/dev/null

# =========================
# 4. Reset ambiente
# =========================
echo "🧹 Limpando containers antigos..."
docker compose down -v

# =========================
# 5. Subir stack
# =========================
echo "🐳 Subindo Langfuse..."
docker compose up -d

# =========================
# 6. Esperar serviços
# =========================
echo "⏳ Aguardando serviços (30s)..."
sleep 30

# =========================
# 7. Status
# =========================
echo ""
echo "📊 Status dos containers:"
docker compose ps

# =========================
# 8. Teste rápido
# =========================
echo ""
echo "🔎 Testando endpoint..."
curl -s http://localhost:3000 > /dev/null

if [ $? -eq 0 ]; then
  echo "✅ Langfuse está respondendo!"
else
  echo "⚠️ Ainda não respondeu (pode estar subindo ainda)"
fi

# =========================
# 9. Infos finais
# =========================
echo ""
echo "🌐 Acesse:"
echo "👉 http://localhost:3000"
echo ""
echo "🧠 Debug se precisar:"
echo "docker compose logs langfuse-web"
echo ""
echo "💾 Postgres do Langfuse:"
echo "👉 localhost:5433"
echo ""