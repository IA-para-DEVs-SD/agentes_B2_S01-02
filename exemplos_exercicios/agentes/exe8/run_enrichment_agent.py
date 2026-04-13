from enrichment_agent import TopicEnrichmentAgent


if __name__ == "__main__":
    print("=" * 60)
    print("  EXERCÍCIO 8 — Enriquecimento com Busca Externa (Exa)")
    print("=" * 60)
    print()

    agent = TopicEnrichmentAgent()
    result = agent.run()

    print("\n" + "=" * 60)
    print("  RELATÓRIO FINAL")
    print("=" * 60)
    print(result)
