import pandas as pd
import json
import sys
import os

REQUIRED_COLUMNS = [
    "ticket_id", "conversation_id", "user_id",
    "speaker", "message", "timestamp", "ticket_status"
]
VALID_SPEAKERS = {"client", "atendente"}
VALID_STATUSES = {"open", "pending", "solved", "closed"}


def load_and_validate_csv(filepath: str) -> pd.DataFrame:
    """
    Carrega o CSV e valida colunas obrigatórias.
    Converte timestamp para datetime.
    Levanta SystemExit com mensagem descritiva em caso de erro.
    """
    if not os.path.exists(filepath):
        print(f"Erro: arquivo '{filepath}' não encontrado.")
        sys.exit(1)

    df = pd.read_csv(filepath)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        print(f"Erro: colunas ausentes no CSV: {', '.join(sorted(missing))}")
        sys.exit(1)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def sort_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ordena por conversation_id (crescente) e timestamp (crescente).
    Retorna novo DataFrame ordenado sem perda de dados.
    """
    return df.sort_values(
        by=["conversation_id", "timestamp"], ascending=[True, True]
    ).reset_index(drop=True)


def get_last_speaker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Para cada conversation_id, retorna DataFrame com colunas:
    [ticket_id, conversation_id, speaker] da última mensagem.
    """
    sorted_df = df.sort_values(by=["conversation_id", "timestamp"], ascending=[True, True])
    last_msgs = sorted_df.groupby("conversation_id").last().reset_index()
    return last_msgs[["ticket_id", "conversation_id", "speaker"]]


def get_final_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Para cada ticket_id, retorna DataFrame com colunas:
    [ticket_id, ticket_status] da última mensagem.
    """
    sorted_df = df.sort_values(by=["ticket_id", "timestamp"], ascending=[True, True])
    last_msgs = sorted_df.groupby("ticket_id").last().reset_index()
    return last_msgs[["ticket_id", "ticket_status"]]


def classify_ticket(last_speaker: str, final_status: str) -> str:
    """
    Aplica regras de classificação:
    - atendente + pending → precisa_follow_up
    - atendente + closed → encerrado
    - client + solved → resolvido
    - atendente + open → risco
    - client + !solved → ativo
    """
    if last_speaker == "atendente" and final_status == "pending":
        return "precisa_follow_up"
    if last_speaker == "atendente" and final_status == "closed":
        return "encerrado"
    if last_speaker == "client" and final_status == "solved":
        return "resolvido"
    if last_speaker == "atendente" and final_status == "open":
        return "risco"
    if last_speaker == "client" and final_status != "solved":
        return "ativo"
    return "ativo"


def classify_all_tickets(last_speakers: pd.DataFrame, final_statuses: pd.DataFrame) -> list[dict]:
    """
    Combina último speaker e status final para classificar todos os tickets.
    Retorna lista de dicts: [{"ticket_id": int, "status": str}, ...]
    """
    # Determine the last speaker per ticket (last conversation's speaker)
    last_speaker_per_ticket = (
        last_speakers
        .sort_values(by="conversation_id", ascending=True)
        .groupby("ticket_id")
        .last()
        .reset_index()[["ticket_id", "speaker"]]
    )

    merged = last_speaker_per_ticket.merge(final_statuses, on="ticket_id")

    result = []
    for _, row in merged.iterrows():
        status = classify_ticket(row["speaker"], row["ticket_status"])
        result.append({"ticket_id": int(row["ticket_id"]), "status": status})

    return result


def suggest_action(classification: str) -> str:
    """
    Mapeia classificação para ação sugerida:
    - precisa_follow_up → send_follow_up
    - risco → monitor
    - encerrado/resolvido/ativo → no_action
    """
    action_map = {
        "precisa_follow_up": "send_follow_up",
        "risco": "monitor",
        "encerrado": "no_action",
        "resolvido": "no_action",
        "ativo": "no_action",
    }
    return action_map.get(classification, "no_action")


def assign_priority(classification: str, final_status: str) -> str:
    """
    Atribui prioridade ao ticket com base na classificação e status final:
    - risco → high
    - pending → medium
    - closed/solved → low
    - demais → medium (default)
    """
    if classification == "risco":
        return "high"
    if final_status == "pending":
        return "medium"
    if final_status in ("closed", "solved"):
        return "low"
    return "medium"


def generate_json(data: list[dict], filepath: str) -> None:
    """
    Serializa lista de dicts em JSON com indent=2 e encoding UTF-8.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def print_reflections(classified_tickets: list[dict], df: pd.DataFrame) -> None:
    """
    Imprime respostas para as 3 perguntas de reflexão baseadas nos dados reais
    processados, citando exemplos concretos de tickets.
    """
    # Build lookup of classification by ticket_id
    classification_map = {t["ticket_id"]: t["status"] for t in classified_tickets}

    # Get final status per ticket for additional context
    sorted_df = df.sort_values(by=["ticket_id", "timestamp"], ascending=[True, True])
    last_per_ticket = sorted_df.groupby("ticket_id").last().reset_index()

    # Collect examples by classification
    follow_up_tickets = [t["ticket_id"] for t in classified_tickets if t["status"] == "precisa_follow_up"]
    encerrado_tickets = [t["ticket_id"] for t in classified_tickets if t["status"] == "encerrado"]
    resolvido_tickets = [t["ticket_id"] for t in classified_tickets if t["status"] == "resolvido"]
    risco_tickets = [t["ticket_id"] for t in classified_tickets if t["status"] == "risco"]
    ativo_tickets = [t["ticket_id"] for t in classified_tickets if t["status"] == "ativo"]

    print("=" * 60)
    print("RESPOSTAS DE REFLEXÃO")
    print("=" * 60)

    # Pergunta 1: Nem todo ghost precisa de follow-up?
    print("\n1) Todo ghost user precisa de follow-up?")
    print("-" * 40)
    print("Não. Nem todo ghost user precisa de follow-up.")
    if encerrado_tickets:
        print(f"   Exemplo: Ticket(s) {encerrado_tickets} foram classificados como 'encerrado'.")
        print("   O atendente foi o último a falar e o ticket foi fechado (closed).")
        print("   Nesses casos, o cliente sumiu mas o atendimento já foi encerrado,")
        print("   então não faz sentido enviar follow-up.")
    if follow_up_tickets:
        print(f"   Já os ticket(s) {follow_up_tickets} precisam de follow-up,")
        print("   pois o atendente foi o último a falar e o status ainda é 'pending'.")
    print("   Conclusão: ghost users com tickets já fechados não precisam de follow-up.")

    # Pergunta 2: Quando é melhor encerrar um ticket?
    print("\n2) Quando é melhor encerrar um ticket?")
    print("-" * 40)
    print("É melhor encerrar um ticket quando o cliente não responde após")
    print("múltiplas tentativas de contato do atendente.")
    if encerrado_tickets:
        enc_id = encerrado_tickets[0]
        ticket_msgs = df[df["ticket_id"] == enc_id].sort_values("timestamp")
        atendente_msgs = ticket_msgs[ticket_msgs["speaker"] == "atendente"]
        print(f"   Exemplo: No ticket {enc_id}, o atendente enviou {len(atendente_msgs)} mensagens")
        print(f"   e o cliente parou de responder. O ticket foi encerrado por falta de resposta.")
    if resolvido_tickets:
        print(f"   Também é adequado encerrar quando o cliente confirma resolução,")
        print(f"   como nos ticket(s) {resolvido_tickets} (status 'solved').")
    print("   Conclusão: encerrar quando há inatividade prolongada do cliente ou resolução confirmada.")

    # Pergunta 3: O status do sistema sempre reflete o comportamento do usuário?
    print("\n3) O status do sistema sempre reflete o comportamento do usuário?")
    print("-" * 40)
    print("Não. O status do sistema nem sempre reflete o comportamento real do usuário.")
    if risco_tickets:
        print(f"   Exemplo: Ticket(s) {risco_tickets} têm status 'open' mas o atendente")
        print("   foi o último a falar — o cliente pode ter abandonado a conversa")
        print("   mesmo com o ticket ainda aberto.")
    if ativo_tickets:
        ativo_example = ativo_tickets[0]
        row = last_per_ticket[last_per_ticket["ticket_id"] == ativo_example].iloc[0]
        print(f"   Exemplo: Ticket {ativo_example} tem status '{row['ticket_status']}' e o cliente")
        print("   foi o último a falar, mas isso não garante que o problema foi resolvido.")
    if follow_up_tickets:
        fu_example = follow_up_tickets[0]
        print(f"   Exemplo: Ticket {fu_example} está como 'pending', mas o cliente já sumiu —")
        print("   o status 'pending' sugere espera ativa, quando na verdade há abandono.")
    print("   Conclusão: o status do sistema é uma visão parcial; é preciso analisar")
    print("   quem falou por último para entender o real estado da interação.")

    print("\n" + "=" * 60)


def main() -> None:
    """
    Orquestra o pipeline completo de detecção de ghost users.
    """
    # 1. Determinar diretório do script e caminho do CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "conversations.csv")

    # 2. Carregar e validar CSV
    df = load_and_validate_csv(csv_path)

    # 3. Ordenar dados
    df = sort_data(df)

    # 4. Identificar último speaker por conversa
    last_speakers = get_last_speaker(df)

    # 5. Identificar status final por ticket
    final_statuses = get_final_status(df)

    # 6. Classificar todos os tickets
    classified_tickets = classify_all_tickets(last_speakers, final_statuses)

    # 7. Para cada ticket, sugerir ação e atribuir prioridade
    # Build a status_final lookup for priority assignment
    status_map = dict(zip(final_statuses["ticket_id"], final_statuses["ticket_status"]))

    ticket_actions = []
    for ticket in classified_tickets:
        action = suggest_action(ticket["status"])
        final_st = status_map.get(ticket["ticket_id"], "open")
        priority = assign_priority(ticket["status"], final_st)
        ticket_actions.append({
            "ticket_id": ticket["ticket_id"],
            "action": action,
            "priority": priority,
        })

    # 8. Gerar conversation_status.json
    conversation_status_path = os.path.join(script_dir, "conversation_status.json")
    generate_json(classified_tickets, conversation_status_path)

    # 9. Gerar ticket_actions.json
    ticket_actions_path = os.path.join(script_dir, "ticket_actions.json")
    generate_json(ticket_actions, ticket_actions_path)

    # 10. Imprimir reflexões
    print_reflections(classified_tickets, df)


if __name__ == "__main__":
    main()
