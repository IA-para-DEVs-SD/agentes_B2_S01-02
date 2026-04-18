"""
Tools para análise de feedbacks de usuários
Cada tool representa uma etapa do processo de análise
"""
import json
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configuração do banco de dados
DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/suporte_ai"
engine = create_engine(DB_URL)

# Cliente Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_feedback(feedback_id: int) -> dict:
    """
    Tool a) Ler um feedback específico do banco de dados
    
    Retorna os dados de um feedback pelo ID.
    """
    query = text("""
        SELECT 
            feedback_id,
            feedback_text,
            created_at,
            channel
        FROM feedbacks
        WHERE feedback_id = :feedback_id
    """)
    
    with engine.begin() as conn:
        row = conn.execute(query, {"feedback_id": feedback_id}).mappings().first()
    
    if not row:
        return {
            "feedback_id": feedback_id,
            "found": False,
            "feedback_text": ""
        }
    
    return {
        "feedback_id": row["feedback_id"],
        "found": True,
        "feedback_text": row["feedback_text"],
        "created_at": str(row["created_at"]),
        "channel": row["channel"]
    }


def analyze_feedback_with_llm(feedback_text: str) -> dict:
    """
    Tool b) Analisar cada feedback com apoio de LLM
    
    Usa o Gemini para analisar o feedback e extrair informações relevantes.
    """
    prompt = f"""
Você é um analisador de feedbacks de usuários.

Analise o seguinte feedback e classifique:

Feedback: "{feedback_text}"

Classifique em:
- categoria: uma das opções: bug, elogio, pagamento, performance, atendimento, outros
- sentimento: uma das opções: positivo, negativo, neutro
- resumo: um resumo curto e objetivo do feedback em uma frase

Responda em JSON com as chaves: categoria, sentimento, resumo.
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema={
                    "type": "object",
                    "properties": {
                        "categoria": {
                            "type": "string",
                            "enum": ["bug", "elogio", "pagamento", "performance", "atendimento", "outros"]
                        },
                        "sentimento": {
                            "type": "string",
                            "enum": ["positivo", "negativo", "neutro"]
                        },
                        "resumo": {
                            "type": "string"
                        }
                    },
                    "required": ["categoria", "sentimento", "resumo"]
                },
                temperature=0.1
            )
        )
        
        result = json.loads(response.text)
        return result
        
    except Exception as e:
        print(f"Erro ao analisar feedback: {e}")
        return {
            "categoria": "outros",
            "sentimento": "neutro",
            "resumo": feedback_text[:100]
        }


def classify_feedback(categoria: str, sentimento: str) -> dict:
    """
    Tool c) Classificar cada feedback
    
    Adiciona classificações adicionais baseadas na análise do LLM.
    """
    # Adiciona prioridade baseada em categoria e sentimento
    priority_map = {
        ("bug", "negativo"): "alta",
        ("pagamento", "negativo"): "alta",
        ("performance", "negativo"): "média",
        ("atendimento", "negativo"): "média",
        ("elogio", "positivo"): "baixa",
    }
    
    key = (categoria, sentimento)
    prioridade = priority_map.get(key, "baixa")
    
    # Adiciona flag de ação necessária
    requer_acao = (
        categoria in ["bug", "pagamento"] and 
        sentimento == "negativo"
    )
    
    return {
        "prioridade": prioridade,
        "requer_acao": requer_acao
    }


def save_analysis_results(feedback_id: int, analysis: dict) -> dict:
    """
    Tool d) Salvar os resultados estruturados
    
    Salva o resultado da análise no banco de dados.
    """
    query = text("""
        INSERT INTO feedback_analysis (
            feedback_id,
            categoria,
            sentimento,
            resumo,
            prioridade,
            requer_acao,
            analyzed_at
        )
        VALUES (
            :feedback_id,
            :categoria,
            :sentimento,
            :resumo,
            :prioridade,
            :requer_acao,
            NOW()
        )
        ON CONFLICT (feedback_id) 
        DO UPDATE SET
            categoria = EXCLUDED.categoria,
            sentimento = EXCLUDED.sentimento,
            resumo = EXCLUDED.resumo,
            prioridade = EXCLUDED.prioridade,
            requer_acao = EXCLUDED.requer_acao,
            analyzed_at = EXCLUDED.analyzed_at
    """)
    
    try:
        with engine.begin() as conn:
            conn.execute(
                query,
                {
                    "feedback_id": feedback_id,
                    "categoria": analysis.get("categoria"),
                    "sentimento": analysis.get("sentimento"),
                    "resumo": analysis.get("resumo"),
                    "prioridade": analysis.get("prioridade"),
                    "requer_acao": analysis.get("requer_acao", False)
                }
            )
        
        return {
            "saved": True,
            "feedback_id": feedback_id
        }
    except Exception as e:
        print(f"Erro ao salvar análise: {e}")
        return {
            "saved": False,
            "feedback_id": feedback_id,
            "error": str(e)
        }


def generate_final_report() -> dict:
    """
    Tool e) Gerar um relatório final com os principais achados
    
    Consolida os resultados salvos no banco e gera estatísticas.
    """
    query = text("""
        SELECT 
            feedback_id,
            categoria,
            sentimento,
            resumo,
            prioridade,
            requer_acao
        FROM feedback_analysis
        ORDER BY feedback_id
    """)
    
    with engine.begin() as conn:
        rows = conn.execute(query).mappings().all()
    
    results = [dict(row) for row in rows]
    total_feedbacks = len(results)
    
    if total_feedbacks == 0:
        return {
            "total_feedbacks": 0,
            "message": "Nenhum feedback analisado ainda"
        }
    
    # Contagem por categoria
    categorias = {}
    for r in results:
        cat = r.get("categoria", "outros")
        categorias[cat] = categorias.get(cat, 0) + 1
    
    # Contagem por sentimento
    sentimentos = {}
    for r in results:
        sent = r.get("sentimento", "neutro")
        sentimentos[sent] = sentimentos.get(sent, 0) + 1
    
    # Contagem por prioridade
    prioridades = {}
    for r in results:
        prior = r.get("prioridade", "baixa")
        prioridades[prior] = prioridades.get(prior, 0) + 1
    
    # Feedbacks que requerem ação
    requer_acao = sum(1 for r in results if r.get("requer_acao", False))
    
    # Principais pontos
    principais_pontos = []
    
    if categorias.get("bug", 0) > 0:
        principais_pontos.append(
            f"Identificados {categorias['bug']} relatos de bugs técnicos"
        )
    
    if categorias.get("performance", 0) > 0:
        principais_pontos.append(
            f"Usuários reportaram {categorias['performance']} problemas de performance"
        )
    
    if categorias.get("pagamento", 0) > 0:
        principais_pontos.append(
            f"Há {categorias['pagamento']} feedbacks sobre problemas de pagamento"
        )
    
    if categorias.get("elogio", 0) > 0:
        principais_pontos.append(
            f"Recebemos {categorias['elogio']} elogios dos usuários"
        )
    
    if sentimentos.get("negativo", 0) > sentimentos.get("positivo", 0):
        principais_pontos.append(
            "Sentimento predominantemente negativo - atenção necessária"
        )
    
    if requer_acao > 0:
        principais_pontos.append(
            f"{requer_acao} feedbacks requerem ação imediata"
        )
    
    report = {
        "total_feedbacks": total_feedbacks,
        "categorias": categorias,
        "sentimentos": sentimentos,
        "prioridades": prioridades,
        "feedbacks_requerem_acao": requer_acao,
        "principais_pontos": principais_pontos,
        "data_geracao": datetime.now().isoformat()
    }
    
    return report


TOOL_MAP = {
    "get_feedback": get_feedback,
    "analyze_feedback_with_llm": analyze_feedback_with_llm,
    "classify_feedback": classify_feedback,
    "save_analysis_results": save_analysis_results,
    "generate_final_report": generate_final_report,
}
