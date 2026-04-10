import pandas as pd


def search_conversations(query: str, engine) -> list[dict]:
    df = pd.read_sql("SELECT * FROM conversations", engine)

    matches = df[df["message"].str.contains(query, case=False, na=False)]

    results = []
    for _, row in matches.head(5).iterrows():
        results.append({
            "source": "conversations",
            "text": row["message"],
            "ticket_id": row.get("ticket_id")
        })

    return results


def search_feedbacks(query: str, engine) -> list[dict]:
    df = pd.read_sql("SELECT * FROM feedbacks", engine)

    matches = df[df["feedback_text"].str.contains(query, case=False, na=False)]

    results = []
    for _, row in matches.head(5).iterrows():
        results.append({
            "source": "feedbacks",
            "text": row["feedback_text"],
            "feedback_id": row.get("feedback_id")
        })

    return results


def load_sensitive_items(engine) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM sensitive_items", engine)


def retrieve_candidate_items(user_input: str, engine) -> list[dict]:
    text = user_input.lower()
    results = []

    keyword_map = {
        "login": ["login", "logar", "acessar", "senha"],
        "payment": ["pagamento", "payment", "cartão", "compra"],
        "performance": ["lento", "lentidão", "travando", "erro", "congela"],
        "delivery": ["entrega", "atrasou", "atrasada"],
        "cancel": ["cancelar", "cancelamento", "assinatura", "pedido"]
    }

    matched_terms = []
    for _, keywords in keyword_map.items():
        for keyword in keywords:
            if keyword in text:
                matched_terms.extend(keywords)
                break

    if not matched_terms:
        matched_terms = [user_input]

    for term in matched_terms:
        results.extend(search_conversations(term, engine))
        results.extend(search_feedbacks(term, engine))

    deduped = []
    seen = set()

    for item in results:
        key = (item["source"], item["text"])
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped[:10]