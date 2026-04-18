#!/bin/bash
# Executa o pipeline completo dos 3 agentes em sequência

echo "🧹 Preparando pasta output..."
mkdir -p output
docker run --rm -v "$(pwd)/output:/app/output" alpine sh -c \
  "chown 1000:1000 /app/output && rm -f /app/output/.scrum_done /app/output/.requirements_done"

echo "🚀 Iniciando pipeline multi-agente..."
docker compose up --build --abort-on-container-exit audit-agent

echo "🛑 Derrubando containers..."
docker compose down

echo ""
echo "📁 Resultados em output/"
ls -la output/*.json 2>/dev/null
