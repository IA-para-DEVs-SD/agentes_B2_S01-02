import asyncio
from dotenv import load_dotenv
from agents import Runner
from agent_react import react_agent

load_dotenv()

async def main():
    print("1. Entrou no main")
    print("2. Vai chamar o Runner")

    result = await Runner.run(
        react_agent,
        "Analise o ticket 1001"
    )

    print("3. Runner terminou")
    print("\nRESPOSTA FINAL:\n")
    print(result.final_output)

if __name__ == "__main__":
    print("0. Iniciando script")
    asyncio.run(main())