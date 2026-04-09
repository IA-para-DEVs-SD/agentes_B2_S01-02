from io import StringIO
import pandas as pd
from sqlalchemy import create_engine

CSV_DATA = """ticket_id,conversation_id,user_id,speaker,message,timestamp,ticket_status
1001,1,101,client,Não consigo fazer login,2026-04-01 09:00,open
1001,1,101,atendente,Você pode tentar redefinir sua senha?,2026-04-01 09:02,pending
1001,1,101,client,Já tentei e não funcionou,2026-04-01 09:05,open
1001,1,101,atendente,Ok vou verificar para você,2026-04-01 09:06,pending
1001,1,101,atendente,Estamos aguardando seu retorno,2026-04-01 12:00,pending
1001,1,101,atendente,Encerrando atendimento por falta de resposta,2026-04-01 18:00,closed
1002,2,102,client,Meu pagamento não passou,2026-04-01 10:00,open
1002,2,102,atendente,Você pode verificar seu cartão?,2026-04-01 10:02,pending
1002,2,102,atendente,Podemos te ajudar com algo mais?,2026-04-01 14:00,pending
1002,2,102,client,Consegui resolver aqui obrigado,2026-04-01 14:10,solved
1003,3,103,client,Minha entrega atrasou,2026-04-01 11:00,open
1003,3,103,atendente,Estamos verificando com a transportadora,2026-04-01 11:03,pending
1003,3,103,client,Ok obrigado,2026-04-01 11:10,open
1003,3,103,atendente,Te aviso assim que tiver atualização,2026-04-01 11:12,pending
1003,3,103,atendente,Atualização: entrega sai hoje,2026-04-01 15:00,pending
1003,3,103,client,Perfeito obrigado!,2026-04-01 15:10,solved
1004,4,104,client,Quero cancelar meu pedido,2026-04-01 12:00,open
1004,4,104,atendente,Posso te ajudar com isso,2026-04-01 12:02,pending
1004,4,104,client,Já resolvi obrigado,2026-04-01 12:10,solved
1005,5,105,client,Não consigo acessar minha conta,2026-04-01 13:00,open
1005,5,105,atendente,Você pode tentar redefinir sua senha?,2026-04-01 13:02,pending
1005,5,105,client,Sumiu aqui o botão,2026-04-01 13:05,open"""

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/suporte_ai"


def main() -> None:
    df = pd.read_csv(StringIO(CSV_DATA))
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    engine = create_engine(DB_URL)
    df.to_sql("conversations", engine, if_exists="append", index=False)
    print(f"{len(df)} linhas carregadas em conversations.")


if __name__ == "__main__":
    main()