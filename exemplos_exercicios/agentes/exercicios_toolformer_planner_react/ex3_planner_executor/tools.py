"""
Tools para o exercício 3 - Planner + Executor
"""
from sqlalchemy import create_engine, text

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5433/suporte_ai"


def get_engine():
    return create_engine(DB_URL)


def load_backlog() -> dict:
    """
    Carrega todas as tarefas do backlog da sprint
    
    Returns:
        dict com lista de tarefas e estatísticas
    """
    engine = get_engine()
    
    query = text("""
        SELECT 
            titulo,
            responsavel,
            status,
            prioridade,
            story_points,
            dias_em_aberto,
            bugs_relacionados,
            sprint
        FROM backlog
        ORDER BY prioridade DESC, dias_em_aberto DESC
    """)
    
    with engine.begin() as conn:
        rows = conn.execute(query).mappings().all()
    
    if not rows:
        return {
            "found": False,
            "tasks": [],
            "total": 0
        }
    
    tasks = []
    for row in rows:
        tasks.append({
            "titulo": row["titulo"],
            "responsavel": row["responsavel"],
            "status": row["status"],
            "prioridade": row["prioridade"],
            "story_points": row["story_points"],
            "dias_em_aberto": row["dias_em_aberto"],
            "bugs_relacionados": row["bugs_relacionados"],
            "sprint": row["sprint"]
        })
    
    # Estatísticas
    total_tasks = len(tasks)
    blocked = sum(1 for t in tasks if t["status"] == "Bloqueado")
    in_progress = sum(1 for t in tasks if t["status"] == "Em progresso")
    todo = sum(1 for t in tasks if t["status"] == "A fazer")
    done = sum(1 for t in tasks if t["status"] == "Concluído")
    total_bugs = sum(t["bugs_relacionados"] for t in tasks)
    total_points = sum(t["story_points"] for t in tasks)
    
    return {
        "found": True,
        "tasks": tasks,
        "total": total_tasks,
        "stats": {
            "blocked": blocked,
            "in_progress": in_progress,
            "todo": todo,
            "done": done,
            "total_bugs": total_bugs,
            "total_points": total_points
        }
    }


# Mapa de tools disponíveis
TOOL_MAP = {
    "load_backlog": load_backlog
}


if __name__ == "__main__":
    # Teste da tool
    print("\n" + "="*60)
    print("🧪 TESTE DA TOOL")
    print("="*60 + "\n")
    
    result = load_backlog()
    
    if result["found"]:
        print(f"✅ Backlog carregado")
        print(f"   Total de tarefas: {result['total']}")
        print(f"   Bloqueadas: {result['stats']['blocked']}")
        print(f"   Em progresso: {result['stats']['in_progress']}")
        print(f"   A fazer: {result['stats']['todo']}")
        print(f"   Concluídas: {result['stats']['done']}")
        print(f"   Total de bugs: {result['stats']['total_bugs']}")
        print(f"   Total de story points: {result['stats']['total_points']}")
        print(f"\n   Primeiras tarefas:")
        for task in result['tasks'][:3]:
            print(f"   - {task['titulo']} ({task['status']}) - {task['responsavel']}")
    else:
        print("❌ Backlog vazio")
    
    print("\n" + "="*60 + "\n")
