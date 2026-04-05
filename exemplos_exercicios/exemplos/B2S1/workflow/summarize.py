from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def detect_sentiment(text: str) -> str:
    lowered = text.lower()
    negative_signals = [
        "não chegou",
        "não resolveram",
        "cancelar",
        "reclamação",
        "problema",
        "atraso",
    ]
    if any(term in lowered for term in negative_signals):
        return "negative"
    return "neutral"


def detect_priority(text: str) -> str:
    lowered = text.lower()
    urgent_signals = ["cancelar", "reclamação", "ainda não resolveram"]
    high_signals = ["não chegou", "atraso", "preciso de ajuda"]

    if any(term in lowered for term in urgent_signals):
        return "urgent"
    if any(term in lowered for term in high_signals):
        return "high"
    return "medium"


def build_key_points(lines: list[str], max_points: int) -> list[str]:
    cleaned = [line.strip() for line in lines if line.strip()]
    customer_lines = [line for line in cleaned if line.lower().startswith("cliente:")]
    points = []

    for line in customer_lines[:max_points]:
        content = line.split(":", 1)[1].strip()
        if not content.endswith("."):
            content += "."
        points.append(content[:1].upper() + content[1:])

    return points


def main() -> None:
    load_dotenv()

    max_points = int(os.getenv("SUMMARY_MAX_POINTS", "4"))
    include_sentiment = parse_bool(os.getenv("SUMMARY_SENTIMENT", "true"), default=True)
    include_priority = parse_bool(os.getenv("SUMMARY_PRIORITY_RULES", "true"), default=True)

    interactions_path = Path("interactions.txt")
    summary_path = Path("summary.json")

    if not interactions_path.exists():
        raise FileNotFoundError("interactions.txt not found")

    raw_text = interactions_path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()

    result = {
        "key_points": build_key_points(lines, max_points),
        "action_needed": "Verificar status do pedido e responder ao cliente.",
    }

    if include_sentiment:
        result["sentiment"] = detect_sentiment(raw_text)

    if include_priority:
        result["priority"] = detect_priority(raw_text)

    summary_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("summary.json updated successfully")


if __name__ == "__main__":
    main()