# Pipeline que conecta os 3 agentes
import sys
import os

# Adiciona os diretórios dos agentes ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class AgentPipeline:
    """
    Orquestra a execução dos 3 agentes em sequência:
    1. Scrum Master: quebra história em tarefas
    2. Analista de Requisitos: identifica requisitos e dependências
    3. Auditor: valida qualidade
    """
    
    def __init__(self):
        # Importa os agentes
        # from agente_01_scrum.agent import ScrumAgent
        # from agente_02_requisitos.agent import RequirementsAgent
        # from agente_03_auditoria.agent import AuditAgent
        
        # self.scrum_agent = ScrumAgent()
        # self.requirements_agent = RequirementsAgent()
        # self.audit_agent = AuditAgent()
        pass
    
    def run(self, user_story: str):
        """
        Executa o pipeline completo
        
        Args:
            user_story: História de usuário para processar
            
        Returns:
            dict com resultados de cada agente
        """
        print("🚀 Iniciando pipeline...")
        
        # Etapa 1: Scrum Master
        print("\n📋 Agente 01 - Scrum Master")
        # tasks = self.scrum_agent.run(user_story)
        tasks = {"placeholder": "tasks from scrum agent"}
        
        # Etapa 2: Analista de Requisitos
        print("\n📝 Agente 02 - Analista de Requisitos")
        # requirements = self.requirements_agent.run(tasks)
        requirements = {"placeholder": "requirements from analyst"}
        
        # Etapa 3: Auditor
        print("\n✅ Agente 03 - Auditor de Qualidade")
        # audit_result = self.audit_agent.run(requirements, tasks)
        audit_result = {"placeholder": "audit results"}
        
        return {
            "tasks": tasks,
            "requirements": requirements,
            "audit": audit_result
        }


if __name__ == "__main__":
    pipeline = AgentPipeline()
    
    user_story = """
    Como usuário, eu quero poder fazer login no sistema
    usando meu email e senha para acessar minha conta.
    """
    
    result = pipeline.run(user_story)
    
    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)
    print(result)
