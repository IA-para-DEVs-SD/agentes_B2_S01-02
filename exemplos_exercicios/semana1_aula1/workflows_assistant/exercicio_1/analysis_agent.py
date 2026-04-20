"""
Agente de análise de tickets de suporte
CSV → SQLite em memória → Agente ReAct com run_sql()

Rode: python agente_sql.py
"""
import sqlite3
import textwrap
from dotenv import load_dotenv
import anthropic

load_dotenv()

# ── 1. DADOS ──────────────────────────────────────────────────────────────────

CSV = """user_id,problema,data,solved_status
1,login,2026-04-01,completed
1,login,2026-04-05,stopped responding
2,pagamento,2026-04-02,completed
3,entrega,2026-04-01,stopped responding
3,entrega,2026-04-03,stopped responding
4,cadastro,2026-04-01,completed
4,pagamento,2026-04-10,completed
5,login,2026-04-02,cancelled
6,entrega,2026-04-02,completed
6,entrega,2026-04-06,completed
7,pagamento,2026-04-03,stopped responding
8,login,2026-04-04,completed
8,cadastro,2026-04-08,completed
9,entrega,2026-04-01,completed
9,entrega,2026-04-07,stopped responding
10,pagamento,2026-04-02,completed
11,login,2026-04-03,stopped responding
11,login,2026-04-06,stopped responding
12,cadastro,2026-04-04,completed
13,entrega,2026-04-05,cancelled
14,pagamento,2026-04-06,completed
14,pagamento,2026-04-09,completed
15,login,2026-04-07,completed
15,login,2026-04-10,completed
16,entrega,2026-04-08,stopped responding
17,pagamento,2026-04-09,cancelled
18,cadastro,2026-04-10,completed
19,login,2026-04-02,completed
19,login,2026-04-05,completed
20,entrega,2026-04-03,stopped responding
20,entrega,2026-04-06,stopped responding"""


# ── 2. BANCO EM MEMÓRIA ───────────────────────────────────────────────────────

def criar_banco() -> sqlite3.Connection:
    """Carrega o CSV num SQLite em memória."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE tickets (
            user_id     INTEGER,
            problema    TEXT,
            data        TEXT,
            solved_status TEXT
        )
    """)
    for linha in CSV.strip().splitlines()[1:]:
        uid, prob, data, status = linha.split(",")
        conn.execute(
            "INSERT INTO tickets VALUES (?, ?, ?, ?)",
            (int(uid), prob, data, status)
        )
    conn.commit()
    return conn


# ── 3. FERRAMENTA ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "run_sql",
        "description": textwrap.dedent("""
            Executa uma query SQL na tabela 'tickets' de suporte ao cliente.

            Schema da tabela:
              user_id      INTEGER  — ID do usuário
              problema     TEXT     — categoria: login, pagamento, entrega, cadastro
              data         TEXT     — data do ticket (YYYY-MM-DD)
              solved_status TEXT    — completed | stopped responding | cancelled
        """).strip(),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query SQL válida contra a tabela 'tickets'"
                }
            },
            "required": ["query"]
        }
    }
]


def run_sql(conn: sqlite3.Connection, query: str) -> str:
    try:
        cur = conn.execute(query)
        rows = cur.fetchall()
        if not rows:
            return "Nenhum resultado encontrado."
        cols = [d[0] for d in cur.description]
        linhas = [" | ".join(cols)]
        linhas.append("-" * len(linhas[0]))
        for r in rows:
            linhas.append(" | ".join(str(v) for v in r))
        return "\n".join(linhas)
    except Exception as e:
        return f"Erro SQL: {e}"


# ── 4. LOOP ReAct ─────────────────────────────────────────────────────────────

SYSTEM = textwrap.dedent("""
    Você é um analista de dados de suporte ao cliente.
    Use a ferramenta run_sql para explorar os dados de tickets e encontrar insights relevantes.

    Seja sistemático:
    1. Comece com uma visão geral (totais por status, por categoria)
    2. Identifique padrões preocupantes
    3. Aprofunde nos casos mais críticos
    4. Ao final, escreva um relatório estruturado com suas conclusões

    Você decide quais queries rodar — não existe sequência pré-definida.
""").strip()


def run_agent(objetivo: str, max_iter: int = 12) -> str:
    client = anthropic.Anthropic()
    conn = criar_banco()
    messages = [{"role": "user", "content": objetivo}]
    iteracao = 0

    print(f"\n{'='*60}")
    print(f"OBJETIVO: {objetivo}")
    print("=" * 60)

    while iteracao < max_iter:
        iteracao += 1
        print(f"\n[Iteração {iteracao}/{max_iter}]")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )

        # Adiciona resposta do modelo ao histórico
        messages.append({"role": "assistant", "content": response.content})

        # Fim do loop
        if response.stop_reason == "end_turn":
            texto = next(
                (b.text for b in response.content if hasattr(b, "text")), ""
            )
            return texto

        # Executa ferramentas
        tool_results = []
        for bloco in response.content:
            if bloco.type != "tool_use":
                continue

            query = bloco.input.get("query", "")
            print(f"  → SQL: {query[:80]}{'...' if len(query) > 80 else ''}")
            resultado = run_sql(conn, query)
            print(f"  ← {resultado[:120]}{'...' if len(resultado) > 120 else ''}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": bloco.id,
                "content": resultado,
            })

        messages.append({"role": "user", "content": tool_results})

    return "[Limite de iterações atingido]"


# ── 5. MAIN ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    relatorio = run_agent(
        "Analise os tickets de suporte e me diga o que precisa de atenção. "
        "Identifique padrões, usuários críticos e categorias problemáticas."
    )

    print(f"\n{'='*60}")
    print("RELATÓRIO FINAL")
    print("=" * 60)
    print(relatorio)