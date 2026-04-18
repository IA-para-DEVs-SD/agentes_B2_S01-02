"""
Exercício 3 - Orchestrator

Coordena a execução do Planner e Executor em sequência.
"""
from planner_agent import PlannerAgent
from executor_agent import ExecutorAgent


def main():
    print("\n" + "="*60)
    print("🎯 PLANNER + EXECUTOR - Exercício 3")
    print("="*60)
    
    # Etapa 1: Planner cria o plano
    print("\n" + "="*60)
    print("ETAPA 1: PLANEJAMENTO")
    print("="*60)
    
    planner = PlannerAgent()
    plan = planner.create_plan("Analise o backlog da sprint")
    
    # Etapa 2: Executor executa o plano
    print("\n" + "="*60)
    print("ETAPA 2: EXECUÇÃO")
    print("="*60)
    
    executor = ExecutorAgent()
    report = executor.execute_plan(plan)
    
    # Resultado final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL")
    print("="*60 + "\n")
    print(report)
    print("\n" + "="*60)
    print("✅ Análise concluída!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
