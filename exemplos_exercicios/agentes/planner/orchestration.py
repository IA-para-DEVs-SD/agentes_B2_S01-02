from agents import Runner
from agent_planner import planner_agent
from agent_exec import executor_agent
import asyncio

async def main():
    user_request = "Analise o backlog da sprint e aponte riscos e recomendações."

    plan_result = await Runner.run(
        planner_agent,
        f"Crie um plano para esta solicitação: {user_request}"
    )

    plan = plan_result.final_output
    print("\nPLANO GERADO:\n")
    print(plan)

    exec_result = await Runner.run(
        executor_agent,
        f"""
        Solicitação do usuário: {user_request}

        Plano gerado:
        {plan}

        Agora execute a análise com base no backlog.
        """
    )

    print("\nRESPOSTA FINAL:\n")
    print(exec_result.final_output)

if __name__ == "__main__":
    asyncio.run(main())