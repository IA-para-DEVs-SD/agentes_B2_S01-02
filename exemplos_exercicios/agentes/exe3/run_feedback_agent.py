from feedback_agent import FeedbackAnalysisAgent


if __name__ == "__main__":
    print("=== Agente de Análise de Feedbacks ===\n")

    agent = FeedbackAnalysisAgent()
    result = agent.run()

    print("\n=== RELATÓRIO FINAL ===")
    print(result)
