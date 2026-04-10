from db import get_engine
from tools import load_sensitive_items, retrieve_candidate_items
from guardrails import is_requesting_internal_notes, filter_safe_items


def build_response(user_input: str, safe_items: list[dict]) -> str:
    if is_requesting_internal_notes(user_input):
        return "I can’t share internal notes or internal instructions, but I can still help with your request."

    if not safe_items:
        return "I couldn’t find any safe supporting context, but I’m happy to help if you describe the issue in a bit more detail."

    top_texts = [item["text"] for item in safe_items[:3]]
    return "Here is some safe context I found: " + " | ".join(top_texts)


def run_agent():
    engine = get_engine()
    sensitive_df = load_sensitive_items(engine)

    print("✅ Guardrail agent started.")
    print("Type 'exit' to stop.\n")

    while True:
        user_input = input("User: ").strip()

        if user_input.lower() == "exit":
            print("Agent: Bye!")
            break

        candidates = retrieve_candidate_items(user_input, engine)
        safe_items, blocked_items = filter_safe_items(candidates, sensitive_df)
        response = build_response(user_input, safe_items)

        print("\n--- Retrieved candidates ---")
        if candidates:
            for item in candidates:
                print(f"[{item['source']}] {item['text']}")
        else:
            print("No candidates found.")

        print("\n--- Blocked by guardrail ---")
        if blocked_items:
            for item in blocked_items:
                print(f"[{item['source']}] {item['text']}")
        else:
            print("No blocked items.")

        print("\n--- Safe items ---")
        if safe_items:
            for item in safe_items:
                print(f"[{item['source']}] {item['text']}")
        else:
            print("No safe items.")

        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    run_agent()