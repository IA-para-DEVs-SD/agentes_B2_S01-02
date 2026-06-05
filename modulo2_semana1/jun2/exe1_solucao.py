from dotenv import load_dotenv
from anthropic import Anthropic
import os

# Carrega variáveis do .env
load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

texto = """
A Copa do Mundo FIFA de 2014 foi realizada no Brasil...
"""

prompt = f"""
Leia o texto abaixo e gere um resumo em no máximo 10 tópicos.

Texto:
{texto}
"""

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=800,
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print(response.content[0].text)