def find_edge_cases(user_story: str):
    return [
        "Usuário sem dados",
        "Sistema sem recursos disponíveis",
        "Erro na API externa"
    ]

def search_qdrant(query: str):
    return ["Caso parecido 1", "Caso parecido 2"]

def analyze_risks(tasks: list):
    return ["Dependência de dados", "Escalabilidade"]

def agent_2_hidden_requirements(agent_1_output: dict):
    story = agent_1_output["user_story"]
    tasks = agent_1_output["tasks"]

    similar_cases = search_qdrant(story)
    edge_cases = find_edge_cases(story)
    risks = analyze_risks(tasks)

    return {
        "similar_cases": similar_cases,
        "edge_cases": edge_cases,
        "risks": risks,
        "gaps": ["Critério de sucesso não definido"]
    }
