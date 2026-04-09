from io import StringIO
import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/suporte_ai"


CONVERSATIONS_CSV = """ticket_id,conversation_id,user_id,speaker,message,timestamp,ticket_status
1001,1,101,client,Não consigo fazer login,2026-04-01 09:00,open
1001,1,101,atendente,Você pode tentar redefinir sua senha,2026-04-01 09:02,pending
1001,1,101,client,Já tentei e não funcionou,2026-04-01 09:05,open

1002,2,102,client,Meu pagamento não passou,2026-04-01 10:00,open
1002,2,102,atendente,Você pode verificar seu cartão,2026-04-01 10:02,pending
1002,2,102,client,Consegui resolver aqui obrigado,2026-04-01 14:10,solved

1003,3,103,client,Minha entrega atrasou,2026-04-01 11:00,open
1003,3,103,atendente,Estamos verificando com a transportadora,2026-04-01 11:03,pending
1003,3,103,client,Ok obrigado,2026-04-01 11:10,solved

1004,4,104,client,Quero cancelar meu pedido,2026-04-01 12:00,open
1004,4,104,atendente,Posso te ajudar com isso,2026-04-01 12:02,pending
1004,4,104,client,Já resolvi obrigado,2026-04-01 12:10,solved

1005,5,105,client,Não consigo acessar minha conta,2026-04-01 13:00,open
1005,5,105,atendente,Tente redefinir a senha por favor,2026-04-01 13:02,pending

1006,6,106,client,O app está travando muito,2026-04-02 09:00,open
1006,6,106,atendente,Pode reiniciar o aplicativo,2026-04-02 09:05,pending

1007,7,107,client,Pagamento recusado sem motivo,2026-04-02 10:00,open
1007,7,107,atendente,Verifique limite do cartão,2026-04-02 10:03,pending

1008,8,108,client,Demora muito para carregar,2026-04-02 11:00,open
1008,8,108,atendente,Estamos analisando lentidão,2026-04-02 11:02,pending

1009,9,109,client,Entrega veio errada,2026-04-02 12:00,open
1009,9,109,atendente,Podemos trocar para você,2026-04-02 12:05,pending

1010,10,110,client,Quero cancelar assinatura,2026-04-02 13:00,open
1010,10,110,atendente,Cancelamento solicitado,2026-04-02 13:05,solved

1011,11,111,client,Não consigo logar no sistema,2026-04-03 09:00,open
1011,11,111,atendente,Tente redefinir senha,2026-04-03 09:02,pending

1012,12,112,client,Erro ao anexar arquivo,2026-04-03 10:00,open
1012,12,112,atendente,Qual tipo de arquivo,2026-04-03 10:02,pending

1013,13,113,client,Compra não finaliza,2026-04-03 11:00,open
1013,13,113,atendente,Verifique método de pagamento,2026-04-03 11:03,pending

1014,14,114,client,Sistema muito lento hoje,2026-04-03 12:00,open
1014,14,114,atendente,Estamos com instabilidade,2026-04-03 12:02,pending

1015,15,115,client,App fechando sozinho,2026-04-03 13:00,open
1015,15,115,atendente,Pode atualizar o app,2026-04-03 13:03,pending

1016,16,116,client,Atendimento foi ótimo,2026-04-04 09:00,solved

1017,17,117,client,Não consigo usar cupom,2026-04-04 10:00,open
1017,17,117,atendente,Verifique validade do cupom,2026-04-04 10:02,pending

1018,18,118,client,Erro ao abrir perfil,2026-04-04 11:00,open
1018,18,118,atendente,Estamos analisando erro,2026-04-04 11:02,pending

1019,19,119,client,Pagamento demorando muito,2026-04-04 12:00,open
1019,19,119,atendente,Pode aguardar alguns minutos,2026-04-04 12:02,pending

1020,20,120,client,Entrega não chegou,2026-04-04 13:00,open
1020,20,120,atendente,Vamos verificar status,2026-04-04 13:03,pending

1021,21,121,client,Quero cancelar pedido urgente,2026-04-05 09:00,open
1021,21,121,atendente,Cancelamento iniciado,2026-04-05 09:02,solved

1022,22,122,client,Login não funciona,2026-04-05 10:00,open
1022,22,122,atendente,Tente redefinir senha,2026-04-05 10:02,pending

1023,23,123,client,App muito lento,2026-04-05 11:00,open
1023,23,123,atendente,Estamos trabalhando nisso,2026-04-05 11:03,pending

1024,24,124,client,Pagamento recusado,2026-04-05 12:00,open
1024,24,124,atendente,Verifique dados do cartão,2026-04-05 12:02,pending

1025,25,125,client,Entrega atrasada novamente,2026-04-05 13:00,open
1025,25,125,atendente,Pedimos desculpas pelo atraso,2026-04-05 13:05,pending

1026,26,126,client,Erro no sistema,2026-04-06 09:00,open
1026,26,126,atendente,Pode detalhar o erro,2026-04-06 09:02,pending

1027,27,127,client,Não consigo acessar minha conta,2026-04-06 10:00,open
1027,27,127,atendente,Tente redefinir senha,2026-04-06 10:02,pending

1028,28,128,client,Compra cancelada sozinha,2026-04-06 11:00,open
1028,28,128,atendente,Estamos verificando isso,2026-04-06 11:03,pending

1029,29,129,client,App travando muito,2026-04-06 12:00,open
1029,29,129,atendente,Reinstale o app por favor,2026-04-06 12:03,pending

1030,30,130,client,Muito satisfeito com o serviço,2026-04-06 13:00,solved
"""


FEEDBACKS_CSV = """feedback_id,feedback_text,created_at,channel
1,O app trava quando tento abrir a tela de pagamento,2026-04-01 10:30,app
2,"Gostei muito da nova interface, ficou mais fácil de usar",2026-04-01 11:00,site
3,O sistema está muito lento para carregar minhas informações,2026-04-01 14:20,app
4,Não consegui finalizar minha compra no site,2026-04-02 09:15,site
5,"Atendimento excelente, resolveram meu problema rapidamente",2026-04-02 10:40,app
6,O aplicativo fecha sozinho quando tento abrir meu perfil,2026-04-02 13:05,app
7,Muito bom adorei a experiência no app,2026-04-03 08:50,app
8,Pagamento recusado sem motivo aparente,2026-04-03 09:30,site
9,Demora muito para carregar a página inicial,2026-04-03 11:10,site
10,O suporte foi atencioso e resolveu tudo,2026-04-03 15:45,app
11,Toda vez que tento atualizar meus dados o app trava,2026-04-04 08:20,app
12,"Achei o novo layout bonito e mais organizado",2026-04-04 09:40,site
13,Não recebi confirmação depois do pagamento,2026-04-04 12:15,site
14,A busca está muito lenta no aplicativo,2026-04-04 14:00,app
15,"Gostei bastante do atendimento, fui bem orientado",2026-04-05 10:10,site
16,O app apresenta erro quando tento anexar um arquivo,2026-04-05 11:25,app
17,Não consegui concluir o pagamento com cartão,2026-04-05 13:50,app
18,Experiência ótima consegui fazer tudo sem dificuldades,2026-04-05 16:05,site
19,O site está muito lento hoje,2026-04-06 08:35,site
20,O aplicativo fecha quando clico em configurações,2026-04-06 09:55,app
21,"Atendimento demorado, mas no final resolveram",2026-04-06 11:40,site
22,Não consegui aplicar meu cupom na hora do pagamento,2026-04-06 14:30,site
23,Gostei da clareza das informações no app,2026-04-07 08:45,app
24,A tela de login demora muito para abrir,2026-04-07 09:20,app
25,O pagamento ficou processando e não concluiu,2026-04-07 10:50,site
26,"Excelente suporte, fui respondido muito rápido",2026-04-07 13:15,app
27,O app travou bem na hora de enviar meus dados,2026-04-08 09:05,app
28,Interface do site ficou confusa depois da atualização,2026-04-08 11:30,site
29,Muito satisfeito com a experiência geral,2026-04-08 15:10,site
30,"A navegação no aplicativo está lenta e às vezes congela",2026-04-08 17:20,app
"""

def load_conversations(engine):
    df = pd.read_csv(StringIO(CONVERSATIONS_CSV))
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df.to_sql("conversations", engine, if_exists="replace", index=False)
    print(f"{len(df)} linhas carregadas em conversations.")


def load_feedbacks(engine):
    df = pd.read_csv(StringIO(FEEDBACKS_CSV))
    df["created_at"] = pd.to_datetime(df["created_at"])

    df.to_sql("feedbacks", engine, if_exists="replace", index=False)
    print(f"{len(df)} linhas carregadas em feedbacks.")


def main():
    engine = create_engine(DB_URL)

    load_conversations(engine)
    load_feedbacks(engine)

    print("\n✅ Ambiente pronto para o exercício!")

if __name__ == "__main__":
    main()