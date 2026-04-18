"""
Tool de busca externa usando Exa API.
Busca boas práticas, referências e padrões relacionados à User Story.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


def search_exa(query: str, num_results: int = 3) -> dict:
    """
    Busca referências externas usando a API Exa.

    Args:
        query: Texto de busca
        num_results: Número de resultados

    Returns:
        dict com resultados da busca
    """
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "EXA_API_KEY não configurada",
            "results": []
        }

    try:
        from exa_py import Exa
        exa = Exa(api_key=api_key)

        response = exa.search_and_contents(
            query=query,
            num_results=num_results,
            use_autoprompt=True,
            text={"max_characters": 500}
        )

        results = []
        for r in response.results:
            results.append({
                "title": r.title,
                "url": r.url,
                "text": r.text[:500] if r.text else ""
            })

        return {
            "status": "success",
            "query": query,
            "results": results
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "results": []
        }
