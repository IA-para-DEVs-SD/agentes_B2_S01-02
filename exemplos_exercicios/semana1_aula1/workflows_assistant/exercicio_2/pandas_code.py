import pandas as pd
import json

# carregar dados
df = pd.read_csv("conversations.csv")

# garantir ordenação
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["ticket_id", "timestamp"])

results = []
actions = []

for ticket_id, group in df.groupby("ticket_id"):
    
    last_row = group.iloc[-1]
    
    last_speaker = last_row["speaker"]
    last_status = last_row["ticket_status"]
    
    # -------------------
    # classificação
    # -------------------
    if last_speaker == "agent" and last_status == "pending":
        status = "precisa_follow_up"
    elif last_speaker == "agent" and last_status == "open":
        status = "risco"
    elif last_speaker == "agent" and last_status == "closed":
        status = "encerrado"
    elif last_speaker == "client" and last_status == "solved":
        status = "resolvido"
    elif last_speaker == "client":
        status = "ativo"
    else:
        status = "unknown"
    
    results.append({
        "ticket_id": int(ticket_id),
        "status": status
    })
    
    # -------------------
    # ação (agente)
    # -------------------
    if status == "precisa_follow_up":
        action = "send_follow_up"
    elif status == "risco":
        action = "monitor"
    else:
        action = "no_action"
    
    actions.append({
        "ticket_id": int(ticket_id),
        "action": action
    })

# salvar outputs
with open("conversation_status.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

with open("ticket_actions.json", "w") as f:
    json.dump(actions, f, indent=2, ensure_ascii=False)

print("Arquivos gerados com sucesso!")
