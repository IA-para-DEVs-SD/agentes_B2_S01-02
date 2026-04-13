import sys
#from gemini_support_agent_toolcalling import SupportTicketAgentToolCalling
from support_agent_toolcalling import SupportTicketAgentToolCalling

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_support_agent.py <ticket_id>")
        sys.exit(1)

    try:
        ticket_id = int(sys.argv[1])
    except ValueError:
        print("Erro: ticket_id precisa ser número inteiro")
        sys.exit(1)

    agent = SupportTicketAgentToolCalling()
    result = agent.run(ticket_id)

    print("\n=== RESULTADO TOOL CALLING ===")
    print(result)