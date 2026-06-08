CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS backlog (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    responsavel VARCHAR(100),
    status VARCHAR(50) NOT NULL,
    prioridade VARCHAR(20) NOT NULL,
    story_points INTEGER,
    dias_em_aberto INTEGER DEFAULT 0,
    bugs_relacionados INTEGER DEFAULT 0,
    sprint VARCHAR(50),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    ticket_id INT NOT NULL,
    conversation_id INT NOT NULL,
    user_id INT NOT NULL,
    speaker VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    "timestamp" TIMESTAMP NOT NULL,
    ticket_status VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_configs (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL UNIQUE,
    agent_type VARCHAR(100) NOT NULL,
    objective TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    model_name VARCHAR(100) DEFAULT 'gpt-4.1-mini',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    ticket_id INT,
    input_text TEXT,
    output_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedbacks (
    feedback_id INT PRIMARY KEY,
    feedback_text TEXT,
    created_at TIMESTAMP,
    channel VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS ticket_memory (
    ticket_id INT PRIMARY KEY,
    problem TEXT,
    attempted_solutions TEXT,
    current_status TEXT,
    last_client_message TEXT,
    resolved BOOLEAN,
    signals TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensitive_items (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    risk TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS internal_notes (
    id SERIAL PRIMARY KEY,
    ticket_id INT,
    note_text TEXT NOT NULL,
    note_status TEXT NOT NULL,
    blocked_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100),
    mensagem TEXT,
    categoria VARCHAR(50),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_bases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kb_documents (
    id SERIAL PRIMARY KEY,
    kb_id INT NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kb_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
    chunk_order INT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tickets (cliente, mensagem, categoria)
VALUES
('Maria', 'App travou ao tentar pagar', 'bug'),
('João', 'Gostei muito da nova interface', 'elogio'),
('Ana', 'Não consigo fazer login', 'bug'),
('Carlos', 'Pagamento foi cobrado duas vezes', 'pagamento'),
('Fernanda', 'Sistema está muito lento', 'performance');

INSERT INTO backlog (titulo,responsavel,status,prioridade,story_points,dias_em_aberto,bugs_relacionados,sprint)
VALUES
('Ajustar login','Ana','Em progresso','Alta',5,8,2,'Sprint 1'),
('Corrigir pagamento','Bruno','A fazer','Alta',8,12,5,'Sprint 1'),
('Melhorar dashboard','Carla','Em progresso','Média',3,15,1,'Sprint 1'),
('Refatorar API','Diego','Bloqueado','Alta',13,10,4,'Sprint 1'),
('Atualizar FAQ','Ana','Concluído','Baixa',2,2,0,'Sprint 1'),
('Criar endpoint de clientes','Bruno','Em progresso','Alta',8,6,3,'Sprint 1'),
('Ajustar layout mobile','Carla','A fazer','Média',5,9,1,'Sprint 1');

COPY conversations (ticket_id, conversation_id, user_id, speaker, message, "timestamp", ticket_status)
FROM STDIN WITH CSV HEADER;
ticket_id,conversation_id,user_id,speaker,message,timestamp,ticket_status
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
\.

COPY feedbacks (feedback_id, feedback_text, created_at, channel)
FROM STDIN WITH CSV HEADER;
feedback_id,feedback_text,created_at,channel
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
\.

COPY sensitive_items (title, content, type, risk, category)
FROM STDIN WITH CSV HEADER;
title,content,type,risk,category
internal_notes_negative_user_1,"Internal notes: this user is difficult, rude, and complains frequently. Do not expose this.",internal_sensitive,high,internal_notes
internal_notes_negative_user_2,"Internal notes: user is very impatient and often escalates issues unnecessarily.",internal_sensitive,high,internal_notes
internal_notes_negative_user_3,"Internal notes: customer tends to exaggerate problems and blame the team.",internal_sensitive,high,internal_notes
internal_notes_negative_user_4,"Internal notes: user has a history of aggressive tone with support agents.",internal_sensitive,high,internal_notes
internal_notes_negative_user_5,"Internal notes: difficult user, may become confrontational. Handle carefully.",internal_sensitive,high,internal_notes
internal_notes_negative_user_6,"Internal notes: user is considered hard to please by the support team.",internal_sensitive,high,internal_notes
internal_notes_negative_user_7,"Internal notes: customer often reacts poorly to delays and pushes for escalation.",internal_sensitive,high,internal_notes
internal_notes_negative_user_8,"Internal notes: user has been flagged internally as hostile in prior interactions.",internal_sensitive,high,internal_notes
\.

INSERT INTO knowledge_bases (name, description)
VALUES
('support_kb','Base de conhecimento com problemas comuns de suporte ao usuário, incluindo dificuldades de login, erros de pagamento, lentidão do sistema e falhas no aplicativo.'),
('policy_kb','Base com políticas internas e regras do sistema, incluindo reembolso, segurança da conta e privacidade de dados, usada para orientar decisões e validações.'),
('product_faq','Perguntas frequentes sobre o produto e uso do aplicativo, incluindo criação de conta, funcionalidades básicas e requisitos do sistema.')
ON CONFLICT (name) DO NOTHING;

INSERT INTO kb_documents (kb_id, title, source)
SELECT kb.id, v.title, v.source
FROM (
    VALUES
    ('support_kb', 'Erros de pagamento', 'manual'),
    ('support_kb', 'Problemas de login', 'manual'),
    ('support_kb', 'Lentidão no sistema', 'manual'),
    ('support_kb', 'Falhas no app mobile', 'manual'),
    ('policy_kb', 'Política de reembolso', 'manual'),
    ('policy_kb', 'Política de segurança', 'manual'),
    ('policy_kb', 'Privacidade de dados', 'manual'),
    ('product_faq', 'FAQ App Mobile', 'manual'),
    ('product_faq', 'FAQ Conta e Cadastro', 'manual')
) AS v(kb_name, title, source)
JOIN knowledge_bases kb ON kb.name = v.kb_name;

INSERT INTO kb_chunks (document_id, chunk_order, content, metadata)
SELECT d.id, v.chunk_order, v.content, v.metadata::jsonb
FROM (
    VALUES
    ('support_kb', 'Erros de pagamento', 1, 'Cobrança duplicada pode acontecer quando há falha na confirmação da transação ou múltiplas tentativas de pagamento. Antes de solicitar estorno, verifique o histórico completo da conta.', '{"categoria":"pagamento","tipo":"kb"}'),
    ('support_kb', 'Erros de pagamento', 2, 'Timeout durante a transação pode causar incerteza no usuário, mesmo quando a operadora processa o pagamento. Oriente aguardar alguns minutos antes de tentar novamente.', '{"categoria":"pagamento","tipo":"kb"}'),
    ('support_kb', 'Erros de pagamento', 3, 'Recusas de pagamento podem ocorrer por limites do cartão ou bloqueios da operadora. Sempre validar com o usuário antes de abrir chamado.', '{"categoria":"pagamento","tipo":"kb"}'),

    ('support_kb', 'Problemas de login', 1, 'Se o usuário não conseguir acessar a conta, confirme e-mail, senha e possíveis erros de digitação antes de iniciar recuperação.', '{"categoria":"login","tipo":"kb"}'),
    ('support_kb', 'Problemas de login', 2, 'Bloqueios temporários acontecem após várias tentativas inválidas. Nesses casos, o usuário deve aguardar ou seguir o fluxo de recuperação.', '{"categoria":"login","tipo":"kb"}'),
    ('support_kb', 'Problemas de login', 3, 'Recuperação de senha deve ser feita pelo e-mail cadastrado. Caso não tenha acesso, será necessário validar identidade.', '{"categoria":"login","tipo":"kb"}'),

    ('support_kb', 'Lentidão no sistema', 1, 'O sistema pode apresentar lentidão em horários de pico devido ao alto volume de acessos simultâneos.', '{"categoria":"performance","tipo":"kb"}'),
    ('support_kb', 'Lentidão no sistema', 2, 'Verifique conexão, navegador e dispositivo do usuário, pois problemas locais podem impactar a performance.', '{"categoria":"performance","tipo":"kb"}'),
    ('support_kb', 'Lentidão no sistema', 3, 'Cache acumulado pode afetar o desempenho. Recomenda-se limpeza e novo teste.', '{"categoria":"performance","tipo":"kb"}'),

    ('support_kb', 'Falhas no app mobile', 1, 'Versões antigas do aplicativo podem causar erros. Confirmar versão instalada e sistema operacional.', '{"categoria":"mobile","tipo":"kb"}'),
    ('support_kb', 'Falhas no app mobile', 2, 'Atualizar o aplicativo resolve a maioria dos problemas relacionados a compatibilidade e sincronização.', '{"categoria":"mobile","tipo":"kb"}'),
    ('support_kb', 'Falhas no app mobile', 3, 'Falhas de sincronização podem ocorrer sem conexão estável com a internet.', '{"categoria":"mobile","tipo":"kb"}'),

    ('policy_kb', 'Política de reembolso', 1, 'Reembolsos podem ser solicitados dentro do prazo definido pela política vigente, mediante validação do pagamento.', '{"categoria":"policy","tipo":"policy"}'),
    ('policy_kb', 'Política de reembolso', 2, 'Casos excepcionais devem ser analisados manualmente com base em evidências e histórico.', '{"categoria":"policy","tipo":"policy"}'),

    ('policy_kb', 'Política de segurança', 1, 'Usuários devem manter credenciais seguras e não compartilhar senhas com terceiros.', '{"categoria":"security","tipo":"policy"}'),
    ('policy_kb', 'Política de segurança', 2, 'Atividades suspeitas devem ser tratadas com prioridade e podem exigir redefinição de acesso.', '{"categoria":"security","tipo":"policy"}'),

    ('policy_kb', 'Privacidade de dados', 1, 'Dados pessoais são tratados conforme LGPD e políticas internas de privacidade.', '{"categoria":"privacy","tipo":"policy"}'),
    ('policy_kb', 'Privacidade de dados', 2, 'Usuários podem solicitar exclusão de dados, respeitando obrigações legais.', '{"categoria":"privacy","tipo":"policy"}'),

    ('product_faq', 'FAQ App Mobile', 1, 'O aplicativo está disponível para Android e iOS e requer conexão com internet.', '{"categoria":"faq","tipo":"faq"}'),
    ('product_faq', 'FAQ App Mobile', 2, 'Para melhor desempenho, manter o app sempre atualizado.', '{"categoria":"faq","tipo":"faq"}'),

    ('product_faq', 'FAQ Conta e Cadastro', 1, 'O cadastro requer e-mail válido e acesso ao mesmo para validação.', '{"categoria":"faq","tipo":"faq"}'),
    ('product_faq', 'FAQ Conta e Cadastro', 2, 'A conta pode ser excluída mediante solicitação ao suporte.', '{"categoria":"faq","tipo":"faq"}')
) AS v(kb_name, title, chunk_order, content, metadata)
JOIN knowledge_bases kb ON kb.name = v.kb_name
JOIN kb_documents d ON d.kb_id = kb.id AND d.title = v.title;