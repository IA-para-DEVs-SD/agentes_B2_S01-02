# Tools para o Agente de Auditoria
# - score_quality: pontua qualidade dos requisitos

import json


# ── Tool definitions (OpenAI Responses API format) ─────────────────────────

TOOLS = [
    {
        "type": "function",
        "name": "score_quality",
        "description": (
            "Avalia a qualidade de um conjunto de requisitos e tarefas, "
            "retornando scores por critério: completude, clareza, "
            "testabilidade e consistência."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "requirements_json": {
                    "type": "string",
                    "description": "JSON stringificado com os requisitos a avaliar.",
                },
                "tasks_json": {
                    "type": "string",
                    "description": "JSON stringificado com as tarefas do backlog.",
                },
            },
            "required": ["requirements_json"],
        },
    },
]


# ── Tool implementations ──────────────────────────────────────────────────

def score_quality(requirements_json: str, tasks_json: str = "[]") -> str:
    """
    Avalia qualidade dos requisitos com heurísticas simples.
    Em produção poderia usar embeddings ou outro modelo.
    """
    try:
        reqs = json.loads(requirements_json)
    except json.JSONDecodeError:
        reqs = {}

    try:
        tasks = json.loads(tasks_json)
    except json.JSONDecodeError:
        tasks = []

    # Heurísticas baseadas na estrutura dos dados
    fr = reqs.get("functional_requirements", [])
    nfr = reqs.get("non_functional_requirements", [])
    risks = reqs.get("risks", [])

    # Completude: tem RFs, RNFs e riscos?
    completude = min(100, len(fr) * 15 + len(nfr) * 15 + len(risks) * 10)

    # Clareza: RFs têm descrição?
    with_desc = sum(1 for r in fr if r.get("description", "").strip())
    clareza = int((with_desc / max(len(fr), 1)) * 100)

    # Testabilidade: RFs têm tarefas relacionadas?
    with_tasks = sum(1 for r in fr if r.get("related_tasks"))
    testabilidade = int((with_tasks / max(len(fr), 1)) * 100)

    # Consistência: tasks referenciadas existem nos RFs?
    task_ids = {t.get("id") or t.get("title") for t in tasks} if tasks else set()
    referenced = set()
    for r in fr:
        referenced.update(r.get("related_tasks", []))
    if task_ids and referenced:
        overlap = len(referenced & task_ids) / max(len(task_ids), 1)
        consistencia = int(overlap * 100)
    else:
        consistencia = 50  # sem dados suficientes

    total = int((completude + clareza + testabilidade + consistencia) / 4)

    result = {
        "total": total,
        "breakdown": {
            "completude": completude,
            "clareza": clareza,
            "testabilidade": testabilidade,
            "consistencia": consistencia,
        },
    }
    return json.dumps(result, ensure_ascii=False)


# ── Dispatcher ─────────────────────────────────────────────────────────────

TOOL_MAP = {
    "score_quality": score_quality,
}


def handle_tool_call(name: str, arguments: dict) -> str:
    """Executa a tool pelo nome e retorna o resultado como string."""
    fn = TOOL_MAP.get(name)
    if fn is None:
        return json.dumps({"error": f"Tool '{name}' não encontrada."})
    return fn(**arguments)
