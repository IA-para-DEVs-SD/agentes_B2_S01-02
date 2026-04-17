from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
Você é um agente Scrum Master.
Sua função é receber uma User Story e transformá-la em uma estrutura clara para o time.

Objetivos:
1. Reescrever a user story de forma mais clara
2. Extrair critérios de aceitação
3. Quebrar em tarefas menores
4. Identificar dependências iniciais
5. Sinalizar dúvidas que ainda precisam de refinamento

Responda sempre em JSON com a estrutura:
{
  "user_story_rewritten": "...",
  "acceptance_criteria": ["...", "..."],
  "tasks": ["...", "..."],
  "dependencies": ["...", "..."],
  "open_questions": ["...", "..."]
}
"""

def scrum_master_agent(user_story: str) -> dict:
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"User Story:\n{user_story}"
            }
        ]
    )

    text_output = response.output_text
    return text_output


if __name__ == "__main__":
    user_story = """
    Como usuário, quero receber recomendações de recursos relevantes
    para encontrar ajuda mais rapidamente.
    """

    result = scrum_master_agent(user_story)
    print(result)
