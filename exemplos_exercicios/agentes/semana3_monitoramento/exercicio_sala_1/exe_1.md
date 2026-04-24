Exercício: Agente de Análise de Texto com Monitoramento
Nível: Básico

# Objetivo
Criar um agente simples usando o SDK da sua preferência (se possível Gemini) que analisa textos e responde perguntas sobre eles. O agente deve ser monitorado com Langfuse (traces) e MLflow (métricas).

# Requisitos
O agente deve ter pelo menos 2 ferramentas:
Ferramenta 1  que faz word_counterConta palavras, caracteres e frases de um texto  e ferramenta 2 language_detector que etecta o idioma do texto (português, inglês, espanhol...). Se você quiser pode fazer um summarizer (bônus) que retorna um resumo em 1 frase do texto recebido.

## O monitoramento deve ter:

- Langfuse Cloud com pelo menos 1 trace por execução
- MLflow local (Docker) com pelo menos as métricas: total_tokens e latency_seconds


LANGFUSE_PUBLIC_KEY=... que você pega da sua conta
LANGFUSE_SECRET_KEY=... que você pega da sua conta

# Casos de teste
Seu agente será testado com estas perguntas:
perguntas = [
    "Quantas palavras tem o texto: 'O céu é azul e o sol brilha forte hoje'?",
    "Em qual idioma está escrito: 'The quick brown fox jumps over the lazy dog'?",
    "Analise o seguinte texto: 'Inteligência artificial está transformando o mundo.'",
]
