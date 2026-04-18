"""
Orquestrador do Pipeline Multi-Agente

Coordena a execução sequencial dos 3 agentes, passando contexto
entre eles via messages[] (short-term memory).

Fluxo:
  User Story → Agente 1 (Scrum Master) → Agente 2 (Req. Ocultos) → Agente 3 (Auditoria) → Relatório Final

Memória:
- Short-term: messages[] passados entre agentes pelo orquestrador
- Long-term: cada agente salva no Qdrant
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.scrum_master import ScrumMasterAgent
from agents.hidden_requirements import HiddenRequirementsAgent
from agents.auditor import AuditorAgent


class Orchestrator:
    def __init__(self):
        self.scrum_master = ScrumMasterAgent()
        self.hidden_requirements = HiddenRequirementsAgent()
        self.auditor = AuditorAgent()

    def run(self, user_story: str, acceptance_criteria: list = None) -> dict:
        """
        Executa o pipeline completo de 3 agentes.
        """
        print("\n" + "="*60)
        print("🚀 PIPELINE MULTI-AGENTE")
        print("="*60)
        print(f"\n📝 User Story: {user_story}")
        if acceptance_criteria:
            print(f"\n📋 Critérios de aceitação:")
            for c in acceptance_criteria:
                print(f"   - {c}")

        # ============================================================
        # ETAPA 1/3: Agente Scrum Master
        # ============================================================
        print("\n" + "="*60)
        print("ETAPA 1/3: SCRUM MASTER")
        print("="*60)

        agent1_output = self.scrum_master.run(user_story, acceptance_criteria)

        print("\n✅ Agente 1 concluído.")
        print(f"   Backlog: {len(agent1_output.get('backlog', []))} tarefas")

        # ============================================================
        # ETAPA 2/3: Agente Requisitos Ocultos
        # Recebe output do Agente 1 via messages[] (short-term memory)
        # ============================================================
        print("\n" + "="*60)
        print("ETAPA 2/3: REQUISITOS OCULTOS")
        print("="*60)

        agent2_output = self.hidden_requirements.run(agent1_output)

        print("\n✅ Agente 2 concluído.")
        print(f"   Requisitos ocultos: {len(agent2_output.get('hidden_requirements', []))}")
        print(f"   Edge cases: {len(agent2_output.get('edge_cases', []))}")
        print(f"   Riscos: {len(agent2_output.get('risks', []))}")
        print(f"   Dependências: {len(agent2_output.get('dependencies', []))}")

        # ============================================================
        # ETAPA 3/3: Agente Auditoria
        # Recebe outputs dos Agentes 1 e 2 via messages[]
        # ============================================================
        print("\n" + "="*60)
        print("ETAPA 3/3: AUDITORIA")
        print("="*60)

        agent3_output = self.auditor.run(agent1_output, agent2_output)

        score = agent3_output.get("quality_score", {})
        print("\n✅ Agente 3 concluído.")
        if score:
            print(f"   Score geral: {score.get('overall', '?')}/10")
        print(f"   Achados: {len(agent3_output.get('audit_findings', []))}")
        print(f"   Sugestões: {len(agent3_output.get('suggestions', []))}")

        # ============================================================
        # RESULTADO CONSOLIDADO
        # ============================================================
        consolidated = {
            "user_story": user_story,
            "acceptance_criteria": acceptance_criteria or [],
            "scrum_master": agent1_output,
            "hidden_requirements": agent2_output,
            "audit": agent3_output,
        }

        return consolidated


def main():
    print("\n" + "="*60)
    print("🎯 MULTI-AGENT USER STORY ANALYZER")
    print("="*60)

    if len(sys.argv) > 1:
        user_story = " ".join(sys.argv[1:])
        acceptance_criteria = []
    else:
        print("\nDigite a User Story (ou Enter para o exemplo):")
        user_input = input("> ").strip()

        if user_input:
            user_story = user_input
            print("\nCritérios de aceitação (um por linha, vazio p/ finalizar):")
            acceptance_criteria = []
            while True:
                c = input("  - ").strip()
                if not c:
                    break
                acceptance_criteria.append(c)
        else:
            user_story = (
                "Como usuário, quero redefinir minha senha "
                "para recuperar o acesso à minha conta."
            )
            acceptance_criteria = [
                "O usuário deve poder solicitar redefinição por e-mail",
                "O link deve expirar após um período",
                "O sistema deve confirmar quando a senha for alterada"
            ]

    orchestrator = Orchestrator()
    result = orchestrator.run(user_story, acceptance_criteria)

    # Exibe resultado
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL CONSOLIDADO")
    print("="*60 + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Salva
    output_path = Path(__file__).parent / "data" / "pipeline_output.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultado salvo em: data/pipeline_output.json")
    print("\n" + "="*60)
    print("✅ Pipeline completo!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
