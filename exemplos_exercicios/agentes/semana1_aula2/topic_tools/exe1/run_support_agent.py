import sys
from gemini_support_agent_basic import SupportTicketAgentBasic


if __name__ == "__main__":

    # valida argumento
    if len(sys.argv) < 2:
        print("Uso: python run_support_agent.py <ticket_id>")
        sys.exit(1)

    try:
        ticket_id = int(sys.argv[1])
    except ValueError:
        print("Erro: ticket_id precisa ser um número")
        sys.exit(1)

    agent = SupportTicketAgentBasic()

    result = agent.run(ticket_id)

    print("\n=== RESULTADO ===")
    print(result)