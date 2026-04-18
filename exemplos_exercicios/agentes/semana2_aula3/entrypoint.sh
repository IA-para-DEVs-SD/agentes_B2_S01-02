#!/bin/bash
# Executa o agente e mantém o container vivo para o healthcheck
python "$@"
echo "✅ Agente finalizado. Mantendo container ativo para dependências..."
sleep infinity
